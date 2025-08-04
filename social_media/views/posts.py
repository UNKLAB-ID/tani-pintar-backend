from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from social_media.filters import PostFilter
from social_media.models import Post
from social_media.paginations import PostCursorPagination
from social_media.serializers import CreatePostSerializer
from social_media.serializers import PostDetailSerializer
from social_media.serializers import PostListSerializer
from social_media.serializers import UpdatePostSerializer


class ListCreatePostView(ListCreateAPIView):
    """
    API view for listing and creating posts with privacy enforcement.

    This view handles both GET (list posts) and POST (create post) operations
    while enforcing privacy settings at the queryset level. It ensures that
    users only see posts they have permission to view based on privacy settings
    and their relationships with post authors.

    Features:
        - Privacy-aware post listing using visible_to_user() filtering
        - Cursor-based pagination for efficient scrolling
        - Full-text search on post content
        - Content filtering to exclude harmful posts
        - Optimized database queries with select_related and prefetch_related

    Permissions:
        - Anonymous users: Can view public posts only
        - Authenticated users: Can view and create posts based on privacy rules
    """

    queryset = Post.objects.none()  # Will be dynamically set in get_queryset()
    pagination_class = PostCursorPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["content"]
    filterset_class = PostFilter
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Get posts visible to the current user based on privacy settings.

        This method implements view-level privacy enforcement by using the
        Post model's custom manager to filter posts based on the requesting
        user's authentication status and relationship with post authors.

        Privacy Filtering:
            - Anonymous users: Only public posts
            - Authenticated users: Public + own posts + friends' posts
            - Content moderation: Excludes potentially harmful posts

        Performance Optimizations:
            - select_related("user"): Reduces database queries for post authors
            - prefetch_related(): Efficiently loads related objects in batch
            - Database indexing on privacy field for fast filtering

        Returns:
            QuerySet[Post]: Privacy-filtered posts optimized for serialization.

        Database Queries:
            - 1 query for posts with privacy filtering
            - 1 query for user data (select_related)
            - 4 queries for related objects (prefetch_related)
        """
        return (
            Post.objects.select_related("user")
            .prefetch_related(
                "postimage_set",
                "comments",
                "likes",
                "saved_posts",
            )
            .exclude(is_potentially_harmful=True)
            .visible_to_user(self.request.user)
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreatePostSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        """
        Set the user for the post when creating.
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post = serializer.save()

        return Response(PostDetailSerializer(post).data, status=status.HTTP_201_CREATED)


class RetrieveUpdateDestroyPostView(RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting individual posts with privacy enforcement.

    This view handles GET (retrieve), PUT/PATCH (update), and DELETE operations
    for individual posts identified by their slug. Privacy enforcement ensures
    users can only access posts they have permission to view, and only post
    authors can modify or delete their posts.

    Features:
        - Privacy-aware post retrieval using visible_to_user() filtering
        - Automatic view tracking for analytics when posts are accessed
        - Owner-only permissions for update and delete operations
        - Optimized database queries for efficient data loading

    Security:
        - Privacy filtering prevents unauthorized access to private posts
        - Ownership validation prevents unauthorized modifications
        - Slug-based lookup provides URL-friendly access without exposing IDs

    URL Pattern:
        - Uses 'slug' field for lookup instead of primary key
        - Example: /api/posts/abc123def/ where 'abc123def' is the post slug
    """  # noqa: E501

    queryset = Post.objects.none()  # Will be dynamically set in get_queryset()
    lookup_field = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Get posts visible to the current user based on privacy settings.

        This method ensures that users can only retrieve posts they have
        permission to view. It applies the same privacy filtering as the
        list view to maintain consistency in privacy enforcement.

        The privacy filtering at the queryset level provides an additional
        security layer - even if a user knows a post's slug, they cannot
        access it unless they have the appropriate permissions.

        Privacy Rules Applied:
            - Anonymous users: Only public posts
            - Authenticated users: Public + own posts + friends' posts
            - Content moderation: Excludes potentially harmful posts

        Returns:
            QuerySet[Post]: Privacy-filtered posts for detail operations.

        Raises:
            Http404: If post doesn't exist or user lacks permission to view it.
        """
        return (
            Post.objects.select_related("user")
            .prefetch_related(
                "postimage_set",
                "comments",
                "likes",
                "saved_posts",
            )
            .exclude(is_potentially_harmful=True)
            .visible_to_user(self.request.user)
        )

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UpdatePostSerializer
        return PostDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)

        if request.user.is_authenticated:
            post = self.get_object()
            post.create_log_view_background(request.user)

        return response

    def update(self, request, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Check permission
        if instance.user != request.user:
            msg = "You do not have permission to update this post."
            raise PermissionDenied(msg)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Refresh instance from database to get updated relationships
        instance.refresh_from_db()

        # Get fresh instance with prefetched relationships for optimal performance
        fresh_instance = self.get_queryset().get(pk=instance.pk)

        # Return response using PostDetailSerializer
        detail_serializer = PostDetailSerializer(
            fresh_instance,
            context={"request": request},
        )
        return Response(detail_serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            msg = "You do not have permission to delete this post."
            raise PermissionDenied(msg)
        super().perform_destroy(instance)
