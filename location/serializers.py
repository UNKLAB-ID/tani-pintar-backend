from rest_framework.serializers import ModelSerializer

from location.models import City
from location.models import Country
from location.models import District
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


class CitySerializer(ModelSerializer):
    province = ProvinceSerializer()

    class Meta:
        model = City
        fields = "__all__"


class DistrictSerializer(ModelSerializer):
    city = CitySerializer()

    class Meta:
        model = District
        fields = "__all__"
