from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework import permissions
from rest_framework.parsers import FormParser
from rest_framework.parsers import JSONParser
from rest_framework.parsers import MultiPartParser
from rest_framework.viewsets import ModelViewSet

from ecommerce.models import Product
from ecommerce.serializers.products import CreateProductSerializer
from ecommerce.serializers.products import ProductDetailSerializer
from ecommerce.serializers.products import ProductListSerializer
from ecommerce.serializers.products import UpdateProductSerializer


class ProductViewSet(ModelViewSet):
    """
    ViewSet for Product model providing full CRUD operations.
    Features:
    - Create, Read, Update, Delete products
    - Filter by category, status, and user
    - Search by name and description
    - Simple main image handling via Product model
    """

    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "status", "user", "approval_status"]
    search_fields = ["name", "description"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return ProductListSerializer
        if self.action == "create":
            return CreateProductSerializer
        if self.action in ["update", "partial_update"]:
            return UpdateProductSerializer
        return ProductDetailSerializer

    def get_queryset(self):
        """
        Get queryset with appropriate filtering based on user.
        - Anonymous users see only approved products
        - Authenticated users can see their own products regardless of approval
        - Staff can see all products
        """
        queryset = super().get_queryset()

        # Optimize queries
        queryset = queryset.select_related("user", "category").prefetch_related(
            "images",
        )

        # Filter based on user permissions
        if self.request.user.is_authenticated:
            if self.request.user.is_staff:
                # Staff can see all products
                return queryset
            # Authenticated users see approved products + their own products
            return queryset.filter(
                Q(approval_status=Product.APPROVAL_APPROVED)
                | Q(user=self.request.user),
            )
        # Anonymous users only see approved products
        return queryset.filter(approval_status=Product.APPROVAL_APPROVED)

    def perform_create(self, serializer):
        """Set the product user to the current user."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Ensure users can only update their own products."""
        product = self.get_object()
        if product.user != self.request.user and not self.request.user.is_staff:
            msg = "You can only update your own products."
            raise permissions.PermissionDenied(msg)
        serializer.save()

    def perform_destroy(self, instance):
        """Ensure users can only delete their own products."""
        if instance.user != self.request.user and not self.request.user.is_staff:
            msg = "You can only delete your own products."
            raise permissions.PermissionDenied(msg)
