from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from ecommerce.models import Product
from ecommerce.paginations import ProductCursorPagination
from ecommerce.permissions import IsVendorOrReadOnly
from ecommerce.serializers.products import CreateProductSerializer
from ecommerce.serializers.products import ProductDetailSerializer
from ecommerce.serializers.products import ProductListSerializer
from ecommerce.serializers.products import UpdateProductSerializer


class ProductListCreateView(ListCreateAPIView):
    """
    View for listing and creating products.
    GET: List products with filtering, search and cursor pagination
    POST: Create new product (requires approved vendor status)
    """

    queryset = Product.objects.all().order_by("-created_at")
    permission_classes = [IsVendorOrReadOnly]
    pagination_class = ProductCursorPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "status", "user", "approval_status"]
    search_fields = ["name", "description"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.request.method == "GET":
            return ProductListSerializer
        return CreateProductSerializer

    def get_queryset(self):
        """
        Get queryset with appropriate filtering based on user.
        - Anonymous users see only approved products
        - Authenticated users can see their own products regardless of approval
        """
        queryset = super().get_queryset()

        # Optimize queries
        queryset = queryset.select_related("user", "category").prefetch_related(
            "images",
            "prices__unit_of_measure",
        )

        # Filter based on user permissions
        if self.request.user.is_authenticated:
            # Authenticated users see approved products + their own products
            return queryset.filter(
                Q(approval_status=Product.APPROVAL_APPROVED)
                | Q(user=self.request.user),
            )
        # Anonymous users only see approved products
        return queryset.filter(approval_status=Product.APPROVAL_APPROVED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(user=request.user)
        read_serializer = ProductDetailSerializer(
            instance,
            context={"request": request},
        )
        headers = self.get_success_headers(read_serializer.data)
        return Response(
            read_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, and deleting individual products.
    GET: Retrieve product details
    PUT/PATCH: Update product (requires approved vendor status and ownership)
    DELETE: Delete product (requires approved vendor status and ownership)
    """

    queryset = Product.objects.all()
    permission_classes = [IsVendorOrReadOnly]
    lookup_field = "uuid"
    lookup_url_kwarg = "pk"

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.request.method == "GET":
            return ProductDetailSerializer
        return UpdateProductSerializer

    def get_queryset(self):
        """Optimize queries and filter based on user permissions."""
        queryset = super().get_queryset()

        # Optimize queries
        queryset = queryset.select_related("user", "category").prefetch_related(
            "images",
            "prices__unit_of_measure",
        )

        # Filter based on user permissions for GET requests
        if self.request.method == "GET":
            if self.request.user.is_authenticated:
                # Authenticated users see approved products + their own products
                return queryset.filter(
                    Q(approval_status=Product.APPROVAL_APPROVED)
                    | Q(user=self.request.user),
                )
            # Anonymous users only see approved products
            return queryset.filter(approval_status=Product.APPROVAL_APPROVED)

        # For modification operations, return all
        # (permissions handled by IsVendorOrReadOnly permission class)
        return queryset

    def perform_update(self, serializer):
        """
        Save product update.
        Vendor validation and ownership handled by permissions.
        """
        product = self.get_object()
        if product.user != self.request.user:
            msg = "You can only update your own products."
            raise permissions.PermissionDenied(msg)

        serializer.save()

    def perform_destroy(self, instance):
        """Ensure users can only delete their own products."""
        if instance.user != self.request.user:
            msg = "You can only delete your own products."
            raise permissions.PermissionDenied(msg)
        instance.delete()
