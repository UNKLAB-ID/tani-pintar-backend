from django.urls import path

from location.views import CountryListAPIView

urlpatterns = [
    path("countries/", CountryListAPIView.as_view(), name="countries"),
]

app_name = "location"
