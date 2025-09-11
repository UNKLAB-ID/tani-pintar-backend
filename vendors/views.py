from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.authentication import JWTAuthentication

from vendors.models import Vendor
from vendors.paginations import VendorCursorPagination
from vendors.serializers import CreateCompanyVendorSerializer
from vendors.serializers import CreateIndividualVendorSerializer
from vendors.serializers import UpdateCompanyVendorSerializer
from vendors.serializers import UpdateIndividualVendorSerializer
from vendors.serializers import VendorDetailSerializer
from vendors.serializers import VendorListSerializer


class VendorListAPIView(ListAPIView):
    """
    List all vendors with filtering, search, and pagination.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    queryset = (
        Vendor.objects.all()
        .select_related(
            "user",
            "province",
            "city",
            "district",
        )
        .filter(review_status=Vendor.STATUS_APPROVED)
    )
    serializer_class = VendorListSerializer
    pagination_class = VendorCursorPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["vendor_type", "review_status", "province", "city"]
    search_fields = ["name", "full_name", "business_name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["-created_at"]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        # Custom filtering for review_status display values
        review_status_param = self.request.query_params.get("review_status")
        if review_status_param:
            # Handle both raw values and display values
            status_mapping = {
                "Pending": Vendor.STATUS_PENDING,
                "Approved": Vendor.STATUS_APPROVED,
                "Rejected": Vendor.STATUS_REJECTED,
                "Resubmission": Vendor.STATUS_RESUBMISSION,
            }
            if review_status_param in status_mapping:
                queryset = queryset.filter(
                    review_status=status_mapping[review_status_param],
                )

        # Custom filtering for vendor_type display values
        vendor_type_param = self.request.query_params.get("vendor_type")
        if vendor_type_param:
            vendor_type_mapping = {
                "individual": Vendor.TYPE_INDIVIDUAL,
                "company": Vendor.TYPE_COMPANY,
            }
            if vendor_type_param.lower() in vendor_type_mapping:
                queryset = queryset.filter(
                    vendor_type=vendor_type_mapping[vendor_type_param.lower()],
                )

        return queryset


class CreateIndividualVendorAPIView(CreateAPIView):
    """
    Create individual vendor.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CreateIndividualVendorSerializer


class CreateCompanyVendorAPIView(CreateAPIView):
    """
    Create company vendor.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CreateCompanyVendorSerializer


class VendorDetailAPIView(RetrieveUpdateAPIView):
    """
    Retrieve and update a single vendor's details.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Vendor.objects.all().select_related(
        "user",
        "user__profile",
        "province",
        "city",
        "district",
    )

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            vendor = self.get_object()
            if vendor.vendor_type == Vendor.TYPE_COMPANY:
                return UpdateCompanyVendorSerializer
            return UpdateIndividualVendorSerializer
        return VendorDetailSerializer


class VendorMeAPIView(RetrieveUpdateAPIView):
    """
    Retrieve and update current user's vendor profile.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = VendorDetailSerializer

    def get_object(self):
        try:
            return Vendor.objects.select_related(
                "user",
                "user__profile",
                "province",
                "city",
                "district",
            ).get(user=self.request.user)
        except Vendor.DoesNotExist:
            msg = "User does not have a vendor profile"
            raise NotFound(msg)  # noqa: B904

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            vendor = self.get_object()
            if vendor.vendor_type == Vendor.TYPE_COMPANY:
                return UpdateCompanyVendorSerializer
            return UpdateIndividualVendorSerializer
        return VendorDetailSerializer
