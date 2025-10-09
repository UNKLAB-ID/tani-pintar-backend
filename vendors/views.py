from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import NotFound
from rest_framework.exceptions import ValidationError
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
    queryset = Vendor.objects.all()
    serializer_class = VendorListSerializer
    pagination_class = VendorCursorPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["vendor_type", "review_status", "province", "city"]
    search_fields = ["name", "full_name", "business_name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["-created_at"]


class CreateIndividualVendorAPIView(CreateAPIView):
    """
    Create individual vendor.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CreateIndividualVendorSerializer

    def create(self, request, *args, **kwargs):
        user = request.user

        # Validate that user does not already have a pending or approved vendor
        if Vendor.objects.filter(
            user=user,
            review_status=Vendor.STATUS_PENDING,
        ).exists():
            msg = "User already has a pending vendor application."
            raise ValidationError({"detail": msg})
        if Vendor.objects.filter(
            user=user,
            review_status=Vendor.STATUS_APPROVED,
        ).exists():
            msg = "User is already an approved vendor."
            raise ValidationError({"detail": msg})

        return super().create(request, *args, **kwargs)


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
