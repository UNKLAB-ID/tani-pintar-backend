from rest_framework import serializers

from .models import Post
from .models import PostComment
from .models import PostImage


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ("id", "image", "created_at")


class PostCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = PostComment
        fields = ("user", "content", "created_at", "updated_at", "parent")

    def get_views_count(self, obj):
        return 10


class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True, source="postimage_set")
    views_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "slug",
            "content",
            "images",
            "views_count",
            "likes_count",
            "comments_count",
            "shared_count",
            "created_at",
            "updated_at",
        )

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_views_count(self, obj):
        return obj.views.count()

    def get_comments_count(self, obj):
        return obj.comments.count()
