from rest_framework import serializers

from thinkflow.models import PlantDisease


class CreatePlantDiseaseSerializer(serializers.Serializer):
    image = serializers.ImageField()

    def create(self, validated_data):
        return PlantDisease.objects.create(**validated_data)


class GetPlantDiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantDisease
        exclude = ("id", "user")
