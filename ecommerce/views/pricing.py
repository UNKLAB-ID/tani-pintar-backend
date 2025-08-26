from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.generics import UpdateAPIView

from ecommerce.models import Product
from ecommerce.models import ProductPrice
from ecommerce.models import UnitOfMeasure
from ecommerce.serializers.pricing import CreateProductPriceSerializer
from ecommerce.serializers.pricing import ProductPriceSerializer
from ecommerce.serializers.pricing import UnitOfMeasureSerializer
from ecommerce.serializers.pricing import UpdateProductPriceSerializer


class UnitOfMeasureListView(ListAPIView):
    """
    View for listing all active units of measure.
    GET: List all active UOMs
    """

    queryset = UnitOfMeasure.objects.filter(is_active=True).order_by("name")
    serializer_class = UnitOfMeasureSerializer
    permission_classes = [permissions.AllowAny]


class UnitOfMeasureDetailView(RetrieveAPIView):
    """
    View for retrieving a specific unit of measure.
    GET: Retrieve UOM details
    """

    queryset = UnitOfMeasure.objects.filter(is_active=True)
    serializer_class = UnitOfMeasureSerializer
    permission_classes = [permissions.AllowAny]


class ProductPriceListCreateView(ListAPIView, CreateAPIView):
    """
    View for listing and creating product prices.
    GET: List prices for a specific product
    POST: Create new price for a product
    """

    serializer_class = ProductPriceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return prices for the specified product."""
        product_id = self.kwargs.get("product_id")
        return ProductPrice.objects.filter(
            product__uuid=product_id,
            is_active=True,
        ).select_related("unit_of_measure")

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.request.method == "POST":
            return CreateProductPriceSerializer
        return ProductPriceSerializer

    def perform_create(self, serializer):
        """Set the product for the price."""
        product_id = self.kwargs.get("product_id")
        product = Product.objects.get(uuid=product_id)

        # Check if user owns the product
        if product.user != self.request.user:
            msg = "You can only add prices to your own products."
            raise PermissionDenied(msg)

        serializer.save(product=product)


class ProductPriceDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    View for retrieving, updating and deleting product prices.
    GET: Retrieve price details
    PUT/PATCH: Update price
    DELETE: Delete price
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return price for the specified product."""
        product_id = self.kwargs.get("product_id")
        return ProductPrice.objects.filter(
            product__uuid=product_id,
        ).select_related("unit_of_measure", "product")

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.request.method in ["PUT", "PATCH"]:
            return UpdateProductPriceSerializer
        return ProductPriceSerializer

    def perform_update(self, serializer):
        """Ensure users can only update prices for their own products."""
        price = self.get_object()
        if price.product.user != self.request.user:
            msg = "You can only update prices for your own products."
            raise PermissionDenied(msg)
        serializer.save()

    def perform_destroy(self, instance):
        """Ensure users can only delete prices for their own products."""
        if instance.product.user != self.request.user:
            msg = "You can only delete prices for your own products."
            raise PermissionDenied(msg)
