from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .filters import PostFilter
from .models import Post
from .models import PostComment
from .paginations import PostCommentCursorPagination
from .paginations import PostCursorPagination
from .serializers import CreatePostSerializer
from .serializers import PostCommentSerializer
from .serializers import PostDetailSerializer
from .serializers import PostSerializer
from .serializers import UpdatePostSerializer




class ListCreatePostView(ListCreateAPIView):
    queryset = Post.objects.select_related("user").prefetch_related(
        "postimage_set",
        "comments",
        "likes",
    )
    pagination_class = PostCursorPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["content"]
    filterset_class = PostFilter
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreatePostSerializer
        return PostSerializer

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
    queryset = Post.objects.select_related("user").prefetch_related(
        "postimage_set",
        "comments",
        "likes",
    )
    lookup_field = "slug"

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

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            msg = "You do not have permission to delete this post."
            raise PermissionDenied(msg)
        super().perform_destroy(instance)


class PostCommentListView(ListCreateAPIView):
    serializer_class = PostCommentSerializer
    pagination_class = PostCommentCursorPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        post_slug = self.kwargs.get("post_slug")
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
