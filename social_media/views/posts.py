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
    queryset = Post.objects.none()  # Will be dynamically set in get_queryset()
    pagination_class = PostCursorPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ["content"]
    filterset_class = PostFilter
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Get posts visible to the current user based on privacy settings
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
    queryset = Post.objects.none()  # Will be dynamically set in get_queryset()
    lookup_field = "slug"
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Get posts visible to the current user based on privacy settings
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

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            msg = "You do not have permission to update this post."
            raise PermissionDenied(msg)
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            msg = "You do not have permission to delete this post."
            raise PermissionDenied(msg)
        super().perform_destroy(instance)
