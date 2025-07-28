from rest_framework import serializers

from accounts.serializers import ProfileDetailSerializer
from core.users.models import User


class UserDetailSerializer(serializers.ModelSerializer):
    profile = ProfileDetailSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "email", "date_joined", "profile"]
