from django.db import IntegrityError
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import Post
from social_media.models import PostLike
from social_media.serializers.post_likes import PostLikeSerializer


class PostLikeCreateView(CreateAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        post_slug = kwargs.get("slug")
        try:
            post = Post.objects.get(slug=post_slug)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            PostLike.objects.create(post=post, user=request.user)
            return Response(
                {"message": "Post liked successfully"},
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError:
            return Response(
                {"error": "You have already liked this post"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PostLikeDestroyView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        post_slug = kwargs.get("slug")
        try:
            post = Post.objects.get(slug=post_slug)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            post_like = PostLike.objects.get(post=post, user=request.user)
            post_like.delete()
            return Response(
                {"message": "Post unliked successfully"},
                status=status.HTTP_200_OK,
            )
        except PostLike.DoesNotExist:
            return Response(
                {"error": "You have not liked this post"},
                status=status.HTTP_400_BAD_REQUEST,
            )
