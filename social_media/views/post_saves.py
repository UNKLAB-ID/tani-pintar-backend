from django.db import IntegrityError
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import Post
from social_media.models import PostSaved


class PostSaveCreateView(CreateAPIView):
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
            PostSaved.objects.create(post=post, user=request.user)
            return Response(
                {"message": "Post saved successfully"},
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError:
            return Response(
                {"error": "You have already saved this post"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PostSaveDestroyView(DestroyAPIView):
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
            post_saved = PostSaved.objects.get(post=post, user=request.user)
            post_saved.delete()
            return Response(
                {"message": "Post unsaved successfully"},
                status=status.HTTP_200_OK,
            )
        except PostSaved.DoesNotExist:
            return Response(
                {"error": "You have not saved this post"},
                status=status.HTTP_400_BAD_REQUEST,
            )
