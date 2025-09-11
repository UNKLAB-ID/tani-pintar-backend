from django.urls import path

from vendors.views import CreateCompanyVendorAPIView
from vendors.views import CreateIndividualVendorAPIView
from vendors.views import VendorDetailAPIView
from vendors.views import VendorListAPIView
from vendors.views import VendorMeAPIView

app_name = "vendors"

urlpatterns = [
    path("", VendorListAPIView.as_view(), name="vendor-list"),
    path(
        "create/individual/",
        CreateIndividualVendorAPIView.as_view(),
        name="vendor-create-individual",
    ),
    path(
        "create/company/",
        CreateCompanyVendorAPIView.as_view(),
        name="vendor-create-company",
    ),
    path("<int:pk>/", VendorDetailAPIView.as_view(), name="vendor-detail"),
    path("me/", VendorMeAPIView.as_view(), name="vendor-me"),
]
