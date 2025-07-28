from rest_framework import serializers

from core.users.serializers import UserDetailSerializer
from social_media.models import PostComment


class PostCommentListSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = PostComment
        fields = (
            "id",
            "content",
            "created_at",
            "updated_at",
            "parent",
            "user",
        )


class CreatePostCommentSerializer(serializers.ModelSerializer):
    content = serializers.CharField(allow_blank=True)  # Allow blank for validation

    class Meta:
        model = PostComment
        fields = ("content", "parent")

    def validate_content(self, value):
        if not value or not value.strip():
            msg = "Content cannot be empty."
            raise serializers.ValidationError(msg)
        return value
