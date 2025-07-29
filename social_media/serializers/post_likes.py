from rest_framework import serializers


class PostLikeSerializer(serializers.Serializer):
    """Simple serializer that returns success message for post likes."""

    def to_representation(self, instance):
        return {"message": "Post liked successfully"}

    def create(self, validated_data):
        return validated_data


class PostDislikeSerializer(serializers.Serializer):
    """Simple serializer that returns success message for post dislikes."""

    def to_representation(self, instance):
        return {"message": "Post disliked successfully"}

    def create(self, validated_data):
        return validated_data
