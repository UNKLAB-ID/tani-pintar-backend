from django.urls import path

from location.views import CountryDetailAPIView
from location.views import CountryListAPIView
from location.views import ProvinceListAPIView

urlpatterns = [
    path("countries/", CountryListAPIView.as_view(), name="countries"),
    path(
        "countries/<str:name>/",
        CountryDetailAPIView.as_view(),
        name="country-detail",
    ),
    path("provinces/", ProvinceListAPIView.as_view(), name="provinces"),
]

app_name = "location"
