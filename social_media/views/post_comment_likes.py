from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from social_media.models import PostComment
from social_media.models import PostCommentLike


class PostCommentLikeCreateView(CreateAPIView):
    """
    API view for creating likes on post comments.

    Allows authenticated users to like comments on posts. Each user can only
    like a comment once, enforced by database unique constraint.

    Supports:
    - POST: Create a new like on a comment

    Features:
    - Authentication required to like comments
    - Prevents duplicate likes with clear error messages
    - Validates comment exists before creating like
    - Returns appropriate HTTP status codes and messages

    URL Parameters:
        post_slug (str): The slug of the post containing the comment
        comment_id (int): The ID of the comment to like

    Returns:
        201: Comment liked successfully
        400: User has already liked this comment
        404: Comment not found
        403: User not authenticated

    Example:
        POST /api/posts/abc123/comments/456/like/
        Response: {"message": "Comment liked successfully"}
    """

    permission_classes = [IsAuthenticated]

    def create(self, request, **kwargs):
        """
        Handle comment like creation.

        Retrieves the comment by post slug and comment ID, then creates
        a like record if the user hasn't already liked the comment.

        Args:
            request: HTTP request object with authenticated user
            **kwargs: Keyword arguments containing post_slug and comment_id

        Returns:
            Response: JSON response with success message or error details

        Raises:
            Http404: If comment doesn't exist or doesn't belong to the post
            IntegrityError: If user has already liked the comment (handled internally)
        """
        post_slug = kwargs.get("post_slug")
        comment_id = kwargs.get("comment_id")

        # Get the comment, ensuring it belongs to the specified post
        comment = get_object_or_404(
            PostComment,
            id=comment_id,
            post__slug=post_slug,
        )

        try:
            PostCommentLike.objects.create(comment=comment, user=request.user)
            return Response(
                {"message": "Comment liked successfully"},
                status=status.HTTP_201_CREATED,
            )
        except IntegrityError:
            return Response(
                {"error": "You have already liked this comment"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class PostCommentLikeDestroyView(DestroyAPIView):
    """
    API view for removing likes from post comments.

    Allows authenticated users to unlike comments they have previously liked.
    Only the user who created the like can remove it.

    Supports:
    - DELETE: Remove an existing like from a comment

    Features:
    - Authentication required to unlike comments
    - Only allows users to unlike their own likes
    - Validates comment exists and user has liked it
    - Returns appropriate HTTP status codes and messages

    URL Parameters:
        post_slug (str): The slug of the post containing the comment
        comment_id (int): The ID of the comment to unlike

    Returns:
        200: Comment unliked successfully
        400: User has not liked this comment
        404: Comment not found
        403: User not authenticated

    Example:
        DELETE /api/posts/abc123/comments/456/unlike/
        Response: {"message": "Comment unliked successfully"}
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, **kwargs):
        """
        Handle comment unlike operation.

        Retrieves the comment by post slug and comment ID, then removes
        the like record if the user has previously liked the comment.

        Args:
            request: HTTP request object with authenticated user
            **kwargs: Keyword arguments containing post_slug and comment_id

        Returns:
            Response: JSON response with success message or error details

        Raises:
            Http404: If comment doesn't exist or doesn't belong to the post
        """
        post_slug = kwargs.get("post_slug")
        comment_id = kwargs.get("comment_id")

        # Get the comment, ensuring it belongs to the specified post
        comment = get_object_or_404(
            PostComment,
            id=comment_id,
            post__slug=post_slug,
        )

        try:
            comment_like = PostCommentLike.objects.get(
                comment=comment,
                user=request.user,
            )
            comment_like.delete()
            return Response(
                {"message": "Comment unliked successfully"},
                status=status.HTTP_200_OK,
            )
        except PostCommentLike.DoesNotExist:
            return Response(
                {"error": "You have not liked this comment"},
                status=status.HTTP_400_BAD_REQUEST,
            )
