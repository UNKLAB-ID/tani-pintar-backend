from rest_framework import serializers

from accounts.serializers import SimpleProfileDetailSerializer
from core.users.models import User
from core.users.serializers import UserDetailSerializer
from social_media.models import Post
from social_media.models import PostImage


class UserSerializer(serializers.ModelSerializer):
    profile = SimpleProfileDetailSerializer()

    class Meta:
        model = User
        fields = ("id", "username", "date_joined", "profile")


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ("id", "image", "created_at")


class CreatePostSerializer(serializers.ModelSerializer):
    MAX_IMAGES = 10  # Maximum number of images that can be uploaded

    user = UserSerializer(read_only=True)
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Post
        fields = (
            "content",
            "privacy",
            "images",
            "user",
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
    user = UserSerializer()

    class Meta:
        model = Post
        fields = (
            "slug",
            "content",
            "privacy",
            "views_count",
            "likes_count",
            "comments_count",
            "shared_count",
            "created_at",
            "updated_at",
            "images",
            "user",
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
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    user = UserDetailSerializer()

    class Meta:
        model = Post
        fields = (
            "slug",
            "content",
            "privacy",
            "images",
            "views_count",
            "likes_count",
            "is_liked",
            "is_saved",
            "comments_count",
            "shared_count",
            "created_at",
            "updated_at",
            "user",
        )

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_views_count(self, obj):
        return obj.views.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_is_saved(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.saved_posts.filter(user=request.user).exists()
        return False


class UpdatePostSerializer(serializers.ModelSerializer):
    MAX_IMAGES = 10  # Maximum number of images that can be uploaded

    privacy = serializers.ChoiceField(
        choices=Post.PRIVACY_CHOICES,
        required=False,
        error_messages={
            "invalid_choice": f"Invalid privacy option. Valid choices are: {', '.join([choice[0] for choice in Post.PRIVACY_CHOICES])}.",  # noqa: E501
        },
    )
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        help_text="List of new images to add to the post",
    )
    delete_image_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of image IDs to delete from the post",
    )
    views_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Post
        fields = (
            "slug",
            "content",
            "privacy",
            "images",
            "delete_image_ids",
            "views_count",
            "likes_count",
            "comments_count",
            "shared_count",
            "created_at",
            "updated_at",
            "user",
        )
        read_only_fields = (
            "slug",
            "views_count",
            "likes_count",
            "comments_count",
            "shared_count",
            "created_at",
            "updated_at",
            "user",
        )

    def validate_privacy(self, value):
        valid_choices = [choice[0] for choice in Post.PRIVACY_CHOICES]
        if value not in valid_choices:
            valid_options = ", ".join(valid_choices)
            msg = f"Invalid privacy option. Valid choices are: {valid_options}"
            raise serializers.ValidationError(msg)
        return value

    def validate_images(self, value):
        if len(value) > self.MAX_IMAGES:
            msg = "You can only upload a maximum of 10 images."
            raise serializers.ValidationError(msg)
        return value

    def validate_delete_image_ids(self, value):
        if not value:
            return value

        # Check if all image IDs belong to the current post
        if self.instance:
            existing_image_ids = self.instance.postimage_set.values_list(
                "id",
                flat=True,
            )
            invalid_ids = [
                img_id for img_id in value if img_id not in existing_image_ids
            ]
            if invalid_ids:
                msg = f"Invalid image IDs: {invalid_ids}. These images don't belong to this post."  # noqa: E501
                raise serializers.ValidationError(msg)

        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)

        # Check total image count after additions and deletions
        if self.instance:
            current_image_count = self.instance.postimage_set.count()
            new_images = attrs.get("images", [])
            delete_image_ids = attrs.get("delete_image_ids", [])

            final_count = current_image_count + len(new_images) - len(delete_image_ids)

            if final_count > self.MAX_IMAGES:
                msg = f"Total images cannot exceed {self.MAX_IMAGES}. Current: {current_image_count}, Adding: {len(new_images)}, Deleting: {len(delete_image_ids)}"  # noqa: E501
                raise serializers.ValidationError(msg)

        return attrs

    def update(self, instance, validated_data):
        images = validated_data.pop("images", None)
        delete_image_ids = validated_data.pop("delete_image_ids", None)

        # Update the post instance with other fields
        instance = super().update(instance, validated_data)

        # Handle image deletions if provided
        if delete_image_ids:
            instance.postimage_set.filter(id__in=delete_image_ids).delete()

        # Handle new image additions if provided
        if images:
            post_images = [PostImage(post=instance, image=image) for image in images]
            PostImage.objects.bulk_create(post_images)

        return instance

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_views_count(self, obj):
        return obj.views.count()

    def get_comments_count(self, obj):
        return obj.comments.count()


class PostListSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True, source="postimage_set")
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    user = UserDetailSerializer()

    class Meta:
        model = Post
        fields = (
            "slug",
            "content",
            "privacy",
            "likes_count",
            "comments_count",
            "is_liked",
            "is_saved",
            "created_at",
            "updated_at",
            "images",
            "user",
        )

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_is_saved(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.saved_posts.filter(user=request.user).exists()
        return False
