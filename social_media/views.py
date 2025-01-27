from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Post
from .models import PostComment
from .serializers import CreatePostSerializer
from .serializers import PostCommentSerializer
from .serializers import PostDetailSerializer
from .serializers import PostSerializer
from .serializers import UpdatePostSerializer


class PostPageNumberPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = "page_size"
    max_page_size = 50


class PostCommentPageNumberPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 50


def index(request):
    return HttpResponse(":)")


class ListCreatePostView(ListCreateAPIView):
    queryset = Post.objects.select_related("user").prefetch_related(
        "postimage_set",
        "comments",
        "likes",
    )
    pagination_class = PostPageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ["content", "user__username"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreatePostSerializer
        return PostSerializer

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
    serializer_class = PostDetailSerializer
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UpdatePostSerializer
        return PostDetailSerializer

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            msg = "You do not have permission to delete this post."
            raise PermissionDenied(msg)
        super().perform_destroy(instance)


class PostCommentListView(ListCreateAPIView):
    serializer_class = PostCommentSerializer
    pagination_class = PostCommentPageNumberPagination
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
