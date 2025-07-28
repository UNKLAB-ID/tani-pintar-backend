from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from social_media.models import Post
from social_media.models import PostComment
from social_media.paginations import PostCommentCursorPagination
from social_media.serializers import PostCommentListSerializer


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
            )
            .select_related("user__profile", "parent")
            .prefetch_related(replies_prefetch)
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
