from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import LoginCode
from accounts.models import Profile
from core.users.models import User


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    id_card_file = serializers.FileField(required=True)
    phone_number = serializers.CharField(required=True)

    def validate_email(self, value):
        if User.objects.filter(username=value).exists():
            msg = "Email already exists"
            raise serializers.ValidationError(msg)

        return value

    def validate_phone_number(self, value):
        if Profile.objects.filter(phone_number=value).exists():
            msg = "Phone number already exists"
            raise serializers.ValidationError(msg)

        return value


class ConfirmRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)

    def validate_email(self, value):
        user = User.objects.filter(username=value)
        if not user.exists():
            msg = "Email does not exist"
            raise serializers.ValidationError(msg)

        if user.first().is_active:
            msg = "User already activated"
            raise serializers.ValidationError(msg)

        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        profile = Profile.objects.filter(email=value)

        if not profile.exists():
            msg = "User not found"
            raise serializers.ValidationError(msg)

        if profile.last().user and not profile.last().user.is_active:
            msg = "User is not active"
            raise serializers.ValidationError(msg)

        return value


class ConfirmLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True)

    def validate_email(self, value):
        profile = Profile.objects.filter(email=value)

        if not profile.exists():
            msg = "User not found"
            raise serializers.ValidationError(msg)

        if profile.last().user and not profile.last().user.is_active:
            msg = "User is not active"
            raise serializers.ValidationError(msg)

        return value

    def validate(self, data):
        user = User.objects.filter(username=data["email"]).first()
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


class RefreshTokenSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        try:
            refresh = RefreshToken(attrs["refresh"])

            new_refresh = RefreshToken.for_user(refresh.user)

            data["refresh"] = str(new_refresh)
        except Exception:  # noqa: BLE001
            msg = "Refresh token is invalid or expired."
            raise ValidationError(msg)  # noqa: B904

        return data
