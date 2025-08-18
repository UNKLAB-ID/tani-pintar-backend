from django.urls import path

from vendors.views import VendorDetailAPIView
from vendors.views import VendorListCreateAPIView
from vendors.views import VendorMeAPIView

app_name = "vendors"

urlpatterns = [
    path("", VendorListCreateAPIView.as_view(), name="vendor-list-create"),
    path("<int:pk>/", VendorDetailAPIView.as_view(), name="vendor-detail"),
    path("me/", VendorMeAPIView.as_view(), name="vendor-me"),
]
