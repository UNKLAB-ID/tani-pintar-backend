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
        fields = (
            "id",
            "user",
            "content",
            "created_at",
            "updated_at",
            "parent",
        )


class CreatePostSerializer(serializers.ModelSerializer):
    MAX_IMAGES = 10  # Maximum number of images that can be uploaded

    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Post
        fields = (
            "content",
            "images",
        )

    def validate_images(self, value):
        if len(value) > self.MAX_IMAGES:
            msg = "You can only upload a maximum of 10 images."
            raise serializers.ValidationError(
                msg,
            )
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        images = validated_data.pop("images", [])

        post = Post.objects.create(user=user, **validated_data)
        post_images = [PostImage(post=post, image=image) for image in images]

        if post_images:
            PostImage.objects.bulk_create(post_images)

        return post


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


class PostDetailSerializer(serializers.ModelSerializer):
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
