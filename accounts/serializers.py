from rest_framework import serializers

from accounts.models import LoginCode
from accounts.models import Profile
from core.users.models import User


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    id_card_file = serializers.FileField(required=True)
    phone_number = serializers.CharField(required=True)

    def validate_email(self, value):
        if Profile.objects.filter(email=value).exists():
            msg = "Email already exists"
            raise serializers.ValidationError(msg)

        return value

    def validate_phone_number(self, value):
        if User.objects.filter(username=value).exists():
            msg = "Phone number already exists"
            raise serializers.ValidationError(msg)

        return value


class ConfirmRegistrationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    code = serializers.CharField(required=True)

    def validate_phone_number(self, value):
        user = User.objects.filter(username=value)
        if not user.exists():
            msg = "Phone number does not exist"
            raise serializers.ValidationError(msg)

        if user.first().is_active:
            msg = "User already activated"
            raise serializers.ValidationError(msg)

        return value


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)

    def validate_phone_number(self, value):
        user = User.objects.filter(username=value)

        if not user.exists():
            msg = "User not found"
            raise serializers.ValidationError(msg)

        if user.last() and not user.last().is_active:
            msg = "User is not active"
            raise serializers.ValidationError(msg)

        return value


class ConfirmLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    code = serializers.CharField(required=True)

    def validate_phone_number(self, value):
        user = User.objects.filter(username=value)

        if not user.exists():
            msg = "User not found"
            raise serializers.ValidationError(msg)

        if user.last() and not user.last().is_active:
            msg = "User is not active"
            raise serializers.ValidationError(msg)

        return value

    def validate(self, data):
        user = User.objects.filter(username=data["phone_number"]).first()
        login_code = (
            LoginCode.objects.filter(user=user, code=data["code"]).last()
            if LoginCode.objects.filter(user=user, code=data["code"]).exists()
            else None
        )

        if not login_code:
            raise serializers.ValidationError({"code": "Invalid code"})

        if login_code.is_expired:
            raise serializers.ValidationError({"code": "Code is expired"})

        return data


class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class ProfileSerializer(serializers.ModelSerializer):
    user = ProfileUserSerializer()
    following_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_followers_count(self, obj):
        return obj.followers.count()

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "full_name",
            "headline",
            "farmer_community",
            "country",
            "city",
            "email",
            "phone_number",
            "profile_type",
            "id_card_file",
            "id_card_validation_status",
            "profile_picture_url",
            "thumbnail_profile_picture_url",
            "cover_picture_url",
            "followers_count",
            "following_count",
            "created_at",
            "updated_at",
        ]


class SimpleProfileDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "full_name",
            "headline",
            "farmer_community",
            "country",
            "city",
            "email",
            "phone_number",
            "profile_type",
            "id_card_file",
            "profile_picture_url",
            "thumbnail_profile_picture_url",
            "cover_picture_url",
        ]
