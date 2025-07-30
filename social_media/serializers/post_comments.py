from rest_framework import serializers

from core.users.serializers import UserDetailSerializer
from social_media.models import PostComment


class PostCommentListSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = PostComment
        fields = (
            "id",
            "content",
            "created_at",
            "updated_at",
            "parent",
            "user",
            "likes_count",
            "is_liked",
        )

    def get_likes_count(self, obj):
        """
        Return the number of likes for this comment.

        Args:
            obj: PostComment instance

        Returns:
            int: Number of likes on the comment
        """
        return obj.likes.count()

    def get_is_liked(self, obj):
        """
        Return whether the current authenticated user has liked this comment.

        Args:
            obj: PostComment instance

        Returns:
            bool: True if current user has liked the comment, False otherwise.
                  Returns False for anonymous users.
        """
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        return obj.likes.filter(user=request.user).exists()


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


class UpdatePostCommentSerializer(serializers.ModelSerializer):
    content = serializers.CharField(allow_blank=True)  # Allow blank for validation

    class Meta:
        model = PostComment
        fields = ("content",)

    def validate_content(self, value):
        if not value or not value.strip():
            msg = "Content cannot be empty."
            raise serializers.ValidationError(msg)
        return value
