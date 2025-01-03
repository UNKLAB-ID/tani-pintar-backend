from rest_framework import serializers

from accounts.models import Profile
from core.users.models import User


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    id_card_file = serializers.FileField(required=True)
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

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
