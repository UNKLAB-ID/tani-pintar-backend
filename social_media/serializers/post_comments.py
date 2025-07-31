from rest_framework import serializers

from core.users.serializers import UserDetailSerializer
from social_media.models import PostComment


class PostCommentListSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    has_replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()

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
            "has_replies",
            "replies_count",
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

    def get_has_replies(self, obj):
        """
        Return whether this comment has any replies.

        Uses the annotated 'has_replies' field from the queryset for optimal
        performance. Falls back to a database query if annotation is not available.

        Args:
            obj: PostComment instance

        Returns:
            bool: True if comment has replies, False otherwise
        """
        # Use annotated field if available (from view's queryset)
        if hasattr(obj, "has_replies"):
            return obj.has_replies

        # Fallback to database query if annotation not available
        return obj.replies.exists()

    def get_replies_count(self, obj):
        """
        Return the number of replies for this comment.

        Uses the annotated 'replies_count' field from the queryset for optimal
        performance. Falls back to a database query if annotation is not available.

        Args:
            obj: PostComment instance

        Returns:
            int: Number of replies on the comment
        """
        # Use annotated field if available (from view's queryset)
        if hasattr(obj, "replies_count"):
            return obj.replies_count

        # Fallback to database query if annotation not available
        return obj.replies.count()


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
