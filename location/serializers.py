from rest_framework.serializers import ModelSerializer

from location.models import Country
from location.models import Province


class CountrySerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class ProvinceSerializer(ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = Province
        fields = "__all__"
