from django.db.models import Exists
from django.db.models import OuterRef
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from social_media.models import Post
from social_media.models import PostComment
from social_media.paginations import PostCommentCursorPagination
from social_media.serializers import PostCommentListSerializer
from social_media.serializers.post_comments import CreatePostCommentSerializer
from social_media.serializers.post_comments import UpdatePostCommentSerializer


class PostCommentListView(ListCreateAPIView):
    """
    API view for listing and creating comments on a specific post.

    Supports:
    - GET: List comments for a post with cursor-based pagination
    - POST: Create a new comment on the post

    Features:
    - Filters out comments from potentially harmful posts
    - Optimized queryset with prefetching to avoid N+1 queries
    - Supports nested replies with proper relationship loading
    - Cursor pagination for efficient large dataset handling
    """

    serializer_class = PostCommentListSerializer
    pagination_class = PostCommentCursorPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreatePostCommentSerializer
        return PostCommentListSerializer

    def list(self, request, *args, **kwargs):
        """
        Override list method to handle potentially harmful posts.

        Returns empty result set for harmful posts to prevent displaying
        inappropriate content while maintaining consistent pagination response format.
        This check is performed before pagination to avoid cursor pagination bugs.

        Args:
            request: HTTP request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments containing post_slug

        Returns:
            Response: Empty paginated response for harmful posts,
                     otherwise standard paginated comment list
        """
        post_slug = self.kwargs.get("post_slug")

        # Check if post is harmful before pagination to avoid cursor pagination bug
        if Post.objects.filter(slug=post_slug, is_potentially_harmful=True).exists():
            return Response(
                {
                    "results": [],
                    "next": None,
                    "previous": None,
                },
            )

        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Build optimized queryset for post comments with performance enhancements.

        Applies multiple database optimizations:
        - Filters comments by post slug and excludes harmful posts
        - Uses select_related for user profiles and parent comments to avoid N+1 queries
        - Uses prefetch_related with custom Prefetch for nested replies optimization
        - Orders by creation time for consistent pagination

        Returns:
            QuerySet: Optimized PostComment queryset with all necessary relationships
                     preloaded for efficient serialization
        """
        post_slug = self.kwargs.get("post_slug")

        # Optimized prefetch for replies with their users and profiles
        replies_prefetch = Prefetch(
            "replies",
            queryset=PostComment.objects.select_related("user__profile").order_by(
                "created_at",
            ),
        )

        return (
            PostComment.objects.filter(
                post__slug=post_slug,
                post__is_potentially_harmful=False,
                parent__isnull=True,  # Only show top-level comments, not replies
            )
            .select_related("user__profile", "parent")
            .prefetch_related(replies_prefetch, "likes__user")
            .annotate(
                has_replies=Exists(
                    PostComment.objects.filter(parent=OuterRef("pk")),
                ),
            )
            .order_by("created_at")
        )

    def perform_create(self, serializer):
        """
        Handle comment creation by associating it with the authenticated user and target post.

        Retrieves the post by slug from URL parameters and automatically sets
        the comment's user to the authenticated request user. Raises 404 if
        the post doesn't exist.

        Args:
            serializer: PostCommentListSerializer instance with validated data

        Raises:
            Http404: If post with the given slug doesn't exist
        """  # noqa: E501
        post_slug = self.kwargs.get("post_slug")
        post = get_object_or_404(Post, slug=post_slug)
        serializer.save(user=self.request.user, post=post)


class PostCommentUpdateView(RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a specific comment.

    Supports:
    - GET: Retrieve comment details
    - PUT/PATCH: Update comment content
    - DELETE: Delete comment

    Features:
    - Only allows comment owner to access their comment
    - Validates that content is not empty on updates
    - Returns 404 if comment doesn't exist or user doesn't own it
    """

    serializer_class = UpdatePostCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieve comment instance ensuring only the owner can access it.

        Returns:
            PostComment: The comment instance if owned by the requesting user

        Raises:
            Http404: If comment doesn't exist or user doesn't own it
        """
        comment_id = self.kwargs.get("comment_id")
        post_slug = self.kwargs.get("post_slug")

        return get_object_or_404(
            PostComment,
            id=comment_id,
            post__slug=post_slug,
            user=self.request.user,
        )


class PostCommentRepliesView(ListAPIView):
    """
    API view for listing replies to a specific comment.

    Supports:
    - GET: List replies for a specific comment with cursor-based pagination

    Features:
    - Filters out replies from potentially harmful posts
    - Optimized queryset with prefetching to avoid N+1 queries
    - Supports nested replies with proper relationship loading
    - Cursor pagination for efficient large dataset handling
    """

    serializer_class = PostCommentListSerializer
    pagination_class = PostCommentCursorPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        """
        Override list method to handle potentially harmful posts.

        Returns empty result set for harmful posts to prevent displaying
        inappropriate content while maintaining consistent pagination response format.
        This check is performed before pagination to avoid cursor pagination bugs.

        Args:
            request: HTTP request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments containing post_slug and comment_id

        Returns:
            Response: Empty paginated response for harmful posts,
                     otherwise standard paginated reply list
        """
        post_slug = self.kwargs.get("post_slug")
        comment_id = self.kwargs.get("comment_id")

        # Check if post is harmful or parent comment doesn't exist
        if (
            Post.objects.filter(slug=post_slug, is_potentially_harmful=True).exists()
            or not PostComment.objects.filter(
                id=comment_id,
                post__slug=post_slug,
                post__is_potentially_harmful=False,
            ).exists()
        ):
            return Response(
                {
                    "results": [],
                    "next": None,
                    "previous": None,
                },
            )

        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Build optimized queryset for comment replies with performance enhancements.

        Applies multiple database optimizations:
        - Filters replies by parent comment ID and post slug
        - Excludes replies from harmful posts
        - Uses select_related for user profiles to avoid N+1 queries
        - Uses prefetch_related for nested replies and likes optimization
        - Orders by creation time for consistent pagination

        Returns:
            QuerySet: Optimized PostComment queryset with all necessary relationships
                     preloaded for efficient serialization
        """
        post_slug = self.kwargs.get("post_slug")
        comment_id = self.kwargs.get("comment_id")

        # Optimized prefetch for nested replies with their users and profiles
        replies_prefetch = Prefetch(
            "replies",
            queryset=PostComment.objects.select_related("user__profile").order_by(
                "created_at",
            ),
        )

        return (
            PostComment.objects.filter(
                parent_id=comment_id,
                post__slug=post_slug,
                post__is_potentially_harmful=False,
            )
            .select_related("user__profile", "parent")
            .prefetch_related(replies_prefetch, "likes__user")
            .annotate(
                has_replies=Exists(
                    PostComment.objects.filter(parent=OuterRef("pk")),
                ),
            )
            .order_by("created_at")
        )
