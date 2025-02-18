from django.urls import path

from location.views import CountryDetailAPIView
from location.views import CountryListAPIView

urlpatterns = [
    path("countries/", CountryListAPIView.as_view(), name="countries"),
    path(
        "countries/<str:name>/",
        CountryDetailAPIView.as_view(),
        name="country-detail",
    ),
]

app_name = "location"
