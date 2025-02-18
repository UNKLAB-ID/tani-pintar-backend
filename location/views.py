from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from location.models import Country
from location.serializers import CountrySerializer


class LocationPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "count"
    max_page_size = 10


class CountryListAPIView(ListAPIView):
    serializer_class = CountrySerializer
    pagination_class = LocationPagination
    queryset = Country.objects.all().order_by("-name")
    permission_classes = [AllowAny]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "code"]
    ordering_fields = ["-name"]


class CountryDetailAPIView(RetrieveAPIView):
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]
    queryset = Country.objects.all()
    lookup_field = "name"
