from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from social_media.models import Post
from social_media.models import PostComment
from social_media.paginations import PostCommentCursorPagination
from social_media.serializers import PostCommentListSerializer


class PostCommentListView(ListCreateAPIView):
    serializer_class = PostCommentListSerializer
    pagination_class = PostCommentCursorPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_slug = self.kwargs.get("post_slug")

        if Post.objects.filter(slug=post_slug, is_potentially_harmful=True):
            return PostComment.objects.none()

        return (
            PostComment.objects.filter(post__slug=post_slug)
            .select_related("user", "parent")
            .prefetch_related("replies", "replies__user")
            .order_by("created_at")
        )

    def perform_create(self, serializer):
        post_slug = self.kwargs.get("post_slug")
        post = get_object_or_404(Post, slug=post_slug)
        serializer.save(user=self.request.user, post=post)
