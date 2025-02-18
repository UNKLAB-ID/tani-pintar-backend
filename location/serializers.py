from rest_framework.serializers import ModelSerializer

from location.models import Country


class CountrySerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"
