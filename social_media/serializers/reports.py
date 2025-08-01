from rest_framework import serializers

from social_media.models import Report


class CreateReportSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new reports.

    This serializer handles the creation of new reports by users.
    The user field is automatically set from the request context,
    and the created_by field is handled by the model's save method.

    Fields:
        post: ID of the post being reported
        reason: Two-letter reason code
        detail_reason: Optional additional explanation
        restrict_user: Whether to hide content from post author
        block_user: Whether to block the post author entirely
    """

    class Meta:
        model = Report
        fields = [
            "post",
            "reason",
            "detail_reason",
            "restrict_user",
            "block_user",
        ]

    def validate_post(self, value):
        """
        Validate that the post exists and can be reported.

        Args:
            value (Post): The post being reported

        Returns:
            Post: The validated post

        Raises:
            ValidationError: If post doesn't exist or is already reported by this user
        """
        user = self.context["request"].user

        # Check if user has already reported this post
        if Report.objects.filter(post=value, user=user).exists():
            raise serializers.ValidationError(
                serializers.ValidationError.default_detail,
            )

        return value

    def create(self, validated_data):
        """
        Create a new report with the current user as the reporter.

        Args:
            validated_data (dict): Validated data from the serializer

        Returns:
            Report: The created report instance
        """
        user = self.context["request"].user
        validated_data["user"] = user
        return super().create(validated_data)


class ReportListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing reports (admin/superuser only).

    This serializer provides comprehensive information about reports
    for administrative purposes. It includes related post and user
    information for context.

    Fields:
        id: Report ID
        post_slug: Slug of the reported post
        post_author: Username of the post author
        reporter: Username of the user who made the report
        reason: Human-readable reason for the report
        detail_reason: Additional explanation from reporter
        restrict_user: Whether reporter wants to hide content
        block_user: Whether reporter wants to block user
        is_approved: Whether report has been approved by moderator
        approved_by: Who approved the report (if applicable)
        created_at: When the report was created
        updated_at: When the report was last updated
    """

    post_slug = serializers.CharField(source="post.slug", read_only=True)
    post_author = serializers.CharField(source="post.user.username", read_only=True)
    reporter = serializers.CharField(source="user.username", read_only=True)
    reason_display = serializers.CharField(source="get_reason_display", read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "post_slug",
            "post_author",
            "reporter",
            "reason",
            "reason_display",
            "detail_reason",
            "restrict_user",
            "block_user",
            "is_approved",
            "approved_by",
            "created_at",
            "updated_at",
        ]


class ReportDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed report view (admin/superuser only).

    This serializer provides full information about a report including
    nested post and user details for administrative review.
    """

    post_data = serializers.SerializerMethodField()
    reporter_data = serializers.SerializerMethodField()
    reason_display = serializers.CharField(source="get_reason_display", read_only=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "post_data",
            "reporter_data",
            "reason",
            "reason_display",
            "detail_reason",
            "restrict_user",
            "block_user",
            "is_approved",
            "approved_by",
            "created_by",
            "created_at",
            "updated_at",
            "updated_by",
        ]

    POST_CONTENT_PREVIEW_LENGTH = 100

    def get_post_data(self, obj):
        """Get basic post information for the report."""
        content = obj.post.content
        if len(content) > self.POST_CONTENT_PREVIEW_LENGTH:
            content = content[: self.POST_CONTENT_PREVIEW_LENGTH] + "..."
        return {
            "id": obj.post.id,
            "slug": obj.post.slug,
            "content": content,
            "author": obj.post.user.username,
            "created_at": obj.post.created_at,
        }

    def get_reporter_data(self, obj):
        """Get basic reporter information for the report."""
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email,
        }


class ApproveReportSerializer(serializers.ModelSerializer):
    """
    Serializer for approving reports (admin/moderator only).

    This serializer handles the approval process for reports,
    allowing moderators to approve or update report status.

    Fields:
        is_approved: Whether the report is approved
    """

    class Meta:
        model = Report
        fields = ["is_approved"]

    def update(self, instance, validated_data):
        """
        Update report approval status and track who approved it.

        Args:
            instance (Report): The report being updated
            validated_data (dict): The validated data

        Returns:
            Report: The updated report instance
        """
        user = self.context["request"].user

        if validated_data.get("is_approved"):
            instance.approve(user)
        else:
            instance.is_approved = validated_data.get(
                "is_approved",
                instance.is_approved,
            )
            instance.updated_by = user.username
            instance.save()

        return instance
