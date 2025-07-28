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
