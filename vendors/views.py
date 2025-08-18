from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from vendors.models import Vendor
from vendors.pagination import VendorCursorPagination
from vendors.serializers import VendorCreateSerializer
from vendors.serializers import VendorDetailSerializer
from vendors.serializers import VendorListSerializer
from vendors.serializers import VendorUpdateSerializer


class VendorListCreateAPIView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = VendorCursorPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["vendor_type", "review_status", "province", "city"]
    search_fields = ["name", "business_name", "full_name"]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return VendorCreateSerializer
        return VendorListSerializer

    def create(self, request, *args, **kwargs):
        if Vendor.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "User already has a vendor profile."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)


class VendorDetailAPIView(generics.RetrieveAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


class VendorMeAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = VendorDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return Vendor.objects.get(user=self.request.user)
        except Vendor.DoesNotExist:
            msg = "User does not have a vendor profile."
            raise NotFound(msg)  # noqa: B904

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return VendorUpdateSerializer
        return VendorDetailSerializer
