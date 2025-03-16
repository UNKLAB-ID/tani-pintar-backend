from django.urls import path

from location.views import CityDetailAPIView
from location.views import CityListAPIView
from location.views import CountryDetailAPIView
from location.views import CountryListAPIView
from location.views import ProvinceDetailAPIView
from location.views import ProvinceListAPIView

urlpatterns = [
    path("countries/", CountryListAPIView.as_view(), name="countries"),
    path(
        "countries/<pk>/",
        CountryDetailAPIView.as_view(),
        name="country-detail",
    ),
    path("provinces/", ProvinceListAPIView.as_view(), name="provinces"),
    path(
        "provinces/<pk>/",
        ProvinceDetailAPIView.as_view(),
        name="province-detail",
    ),
    path("cities/", CityListAPIView.as_view(), name="cities"),
    path("cities/<pk>/", CityDetailAPIView.as_view(), name="city-detail"),
]

app_name = "location"
