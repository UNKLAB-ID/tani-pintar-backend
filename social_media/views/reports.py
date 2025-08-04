from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from social_media.models import Post
from social_media.serializers import CreateReportSerializer


class PostReportView(generics.CreateAPIView):
    """
    Create a report for a specific post using the post slug.

    This is a convenience view that allows reporting a post by its slug
    without needing to specify the post ID in the request body.

    Permissions:
        - Must be authenticated

    URL Parameters:
        - slug: The post slug to report

    Request Body:
        {
            "reason": "<two_letter_code>",
            "detail_reason": "<optional_explanation>",
            "restrict_user": <boolean>,
            "block_user": <boolean>
        }

    Response:
        201: Report created successfully
        400: Invalid data or duplicate report
        401: Not authenticated
        404: Post not found
    """

    serializer_class = CreateReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_post(self):
        """
        Get the post to be reported based on slug.

        Returns:
            Post: The post to be reported

        Raises:
            Http404: If post is not found
        """
        slug = self.kwargs.get("slug")
        return get_object_or_404(Post, slug=slug)

    def create(self, request, *args, **kwargs):
        """
        Create a report for the specified post.

        Args:
            request: The HTTP request
            *args: Additional arguments
            **kwargs: Additional keyword arguments

        Returns:
            Response: Success or error response
        """
        post = self.get_post()

        # Add post to request data
        data = request.data.copy()
        data["post"] = post.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {
                "message": f"Report for post '{post.slug}' submitted successfully.",
                "report_id": serializer.instance.id,
            },
            status=status.HTTP_201_CREATED,
        )

    def perform_create(self, serializer):
        """
        Save the report with the current user as the reporter.

        Args:
            serializer: The validated serializer instance
        """
        serializer.save(user=self.request.user)
