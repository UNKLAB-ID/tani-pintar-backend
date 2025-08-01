from rest_framework import generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from social_media.models import Report, Post
from social_media.serializers import (
    CreateReportSerializer,
    ReportListSerializer,
    ReportDetailSerializer,
    ApproveReportSerializer,
)


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission that only allows superusers to access report lists and details.
    Regular users can only create reports.
    """

    def has_permission(self, request, view):
        """
        Check if user has permission to access the view.
        
        Args:
            request: The HTTP request
            view: The view being accessed
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # Allow POST (create) for authenticated users
        if request.method == 'POST':
            return request.user.is_authenticated
        
        # Only allow list/detail views for superusers
        return request.user.is_authenticated and request.user.is_superuser


class CreateReportView(generics.CreateAPIView):
    """
    Create a new report for a post.

    This view allows authenticated users to report posts that violate
    community guidelines. Each user can only report a post once.

    Permissions:
        - Must be authenticated
        - Can only report posts once

    Request Body:
        {
            "post": <post_id>,
            "reason": "<two_letter_code>",
            "detail_reason": "<optional_explanation>",
            "restrict_user": <boolean>,
            "block_user": <boolean>
        }

    Response:
        201: Report created successfully
        400: Invalid data or duplicate report
        401: Not authenticated
    """

    serializer_class = CreateReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Save the report with the current user as the reporter.

        Args:
            serializer: The validated serializer instance
        """
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Override create to provide custom response messages.

        Args:
            request: The HTTP request
            *args: Additional arguments
            **kwargs: Additional keyword arguments

        Returns:
            Response: Success or error response
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            {
                "message": "Report submitted successfully. Our team will review it.",
                "report_id": serializer.instance.id,
            },
            status=status.HTTP_201_CREATED,
        )


class ReportListView(generics.ListAPIView):
    """
    List all reports (superuser only).

    This view allows superusers to see all reports in the system
    for moderation purposes. Regular users cannot access this endpoint.

    Permissions:
        - Must be superuser

    Query Parameters:
        - reason: Filter by report reason code
        - is_approved: Filter by approval status (true/false)
        - ordering: Order by field (default: -created_at)

    Response:
        200: List of reports
        403: Not a superuser
    """

    serializer_class = ReportListSerializer
    permission_classes = [IsSuperUserOrReadOnly]
    filterset_fields = ["reason", "is_approved"]
    ordering_fields = ["created_at", "updated_at", "reason"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Get all reports with related post and user data.

        Returns:
            QuerySet: All reports with optimized queries
        """
        return Report.objects.select_related("post", "user", "post__user").all()


class ReportDetailView(generics.RetrieveAPIView):
    """
    Get detailed information about a specific report (superuser only).

    This view allows superusers to see full details of a report
    including related post and user information.

    Permissions:
        - Must be superuser

    Response:
        200: Report details
        403: Not a superuser
        404: Report not found
    """

    serializer_class = ReportDetailSerializer
    permission_classes = [IsSuperUserOrReadOnly]
    lookup_field = "id"

    def get_queryset(self):
        """
        Get reports with related data.

        Returns:
            QuerySet: Reports with optimized queries
        """
        return Report.objects.select_related("post", "user", "post__user").all()


class ApproveReportView(generics.UpdateAPIView):
    """
    Approve or update a report (superuser only).

    This view allows superusers to approve reports and update their status.
    When a report is approved, it can trigger additional moderation actions.

    Permissions:
        - Must be superuser

    Request Body:
        {
            "is_approved": <boolean>
        }

    Response:
        200: Report updated successfully
        403: Not a superuser
        404: Report not found
    """

    serializer_class = ApproveReportSerializer
    permission_classes = [IsSuperUserOrReadOnly]
    lookup_field = "id"

    def get_queryset(self):
        """
        Get reports that can be updated.

        Returns:
            QuerySet: All reports
        """
        return Report.objects.all()

    def update(self, request, *args, **kwargs):
        """
        Update report approval status.

        Args:
            request: The HTTP request
            *args: Additional arguments
            **kwargs: Additional keyword arguments

        Returns:
            Response: Success response with updated report data
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        action_taken = "approved" if serializer.validated_data.get("is_approved") else "updated"
        
        return Response({
            "message": f"Report {action_taken} successfully.",
            "report": ReportDetailSerializer(instance).data,
        })


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
