from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from location.models import City
from location.models import Country
from location.models import District
from location.models import Province
from location.serializers import CitySerializer
from location.serializers import CountrySerializer
from location.serializers import DistrictSerializer
from location.serializers import ProvinceSerializer


class LocationPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "count"
    max_page_size = 10


class BaseLocationListAPIView(ListAPIView):
    pagination_class = LocationPagination
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    ordering_fields = ["-name"]


class BaseLocationDetailAPIView(RetrieveAPIView):
    permission_classes = [AllowAny]


class CountryListAPIView(BaseLocationListAPIView):
    serializer_class = CountrySerializer
    queryset = Country.objects.all().order_by("-name")
    search_fields = ["name", "code"]
    filterset_fields = ["name"]


class CountryDetailAPIView(BaseLocationDetailAPIView):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()


class ProvinceListAPIView(BaseLocationListAPIView):
    serializer_class = ProvinceSerializer
    queryset = Province.objects.all().order_by("-name").prefetch_related("country")
    search_fields = ["name"]
    filterset_fields = ["name", "country__name", "country__id"]


class ProvinceDetailAPIView(BaseLocationDetailAPIView):
    serializer_class = ProvinceSerializer
    queryset = Province.objects.all()


class CityListAPIView(BaseLocationListAPIView):
    serializer_class = CitySerializer
    queryset = (
        City.objects.all()
        .order_by("-name")
        .prefetch_related("province")
        .prefetch_related("province__country")
    )
    search_fields = ["name"]
    filterset_fields = [
        "name",
        "province__name",
        "province__id",
        "province__country__name",
        "province__country__id",
    ]


class CityDetailAPIView(BaseLocationDetailAPIView):
    serializer_class = CitySerializer
    queryset = City.objects.all()


class DistrictListAPIView(BaseLocationListAPIView):
    serializer_class = DistrictSerializer
    queryset = (
        District.objects.all()
        .order_by("-name")
        .prefetch_related("city")
        .prefetch_related("city__province")
        .prefetch_related("city__province__country")
    )
    search_fields = ["name"]
    filterset_fields = [
        "name",
        "city__name",
        "city__id",
        "city__province__name",
        "city__province__id",
        "city__province__country__name",
        "city__province__country__id",
    ]


class DistrictDetailAPIView(BaseLocationDetailAPIView):
    serializer_class = DistrictSerializer
    queryset = District.objects.all()
