from rest_framework import serializers

from core.users.models import User
from ecommerce.models import Product
from ecommerce.models import ProductCategory
from ecommerce.models import ProductImage
from ecommerce.serializers.categories import CategorySimpleSerializer
from ecommerce.serializers.uom import ProductPriceListSerializer


class UserSimpleSerializer(serializers.ModelSerializer):
    """
    Simple user serializer for product views.
    Contains only essential user information.
    """

    class Meta:
        model = User
        fields = ["id", "username"]
        read_only_fields = ["id", "username"]


class ProductImageDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductImage detail view.
    Used for retrieving and displaying image details.
    """

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "caption",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ProductImageListSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductImage list view.
    Lightweight serializer for listing images.
    """

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "caption",
        ]
        read_only_fields = ["id"]


class CreateProductSerializer(serializers.Serializer):
    """
    Serializer for creating new products.
    Handles product creation with main image field.
    """

    image = serializers.ImageField(required=True)
    name = serializers.CharField(max_length=255, required=True)
    category = serializers.PrimaryKeyRelatedField(
        required=True,
        queryset=ProductCategory.objects.all(),
    )
    description = serializers.CharField(required=True)
    condition = serializers.CharField(max_length=50, required=True)
    # harga satuan produk
    available_stock = serializers.IntegerField(required=True, min_value=0)
    weight = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        min_value=0.0,
    )
    weight_unit = serializers.CharField(max_length=10, required=True)

    def validate_condition(self, value):
        if not value:
            msg = "Condition cannot be empty."
            raise serializers.ValidationError(msg)

        condition_choices = [condition for condition, _ in Product.CONDITION_CHOICES]
        if value not in condition_choices:
            msg = f"Invalid condition: {value}. Valid choices are: {condition_choices}"
            raise serializers.ValidationError(msg)

        return value

    def validate_weight_unit(self, value):
        if not value:
            msg = "Weight unit cannot be empty."
            raise serializers.ValidationError(msg)

        weight_unit_choices = [unit for unit, _ in Product.WEIGHT_CHOICES]
        if value not in weight_unit_choices:
            msg = f"Invalid weight unit: {value}. Valid choices are: {weight_unit_choices}"  # noqa: E501
            raise serializers.ValidationError(msg)

        return value


class UpdateProductSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing products.
    Allows updating product fields and main image.
    """

    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "image",
            "available_stock",
            "status",
        ]

    def validate_available_stock(self, value):
        """Validate that stock is non-negative."""
        if value < 0:
            msg = "Stock cannot be negative."
            raise serializers.ValidationError(msg)
        return value


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for product detail view.
    Includes all product information with nested images and pricing.
    """

    user = UserSimpleSerializer(read_only=True)
    category = CategorySimpleSerializer(read_only=True)
    images = ProductImageDetailSerializer(many=True, read_only=True)
    prices = ProductPriceListSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "uuid",
            "user",
            "category",
            "name",
            "slug",
            "description",
            "image",
            "available_stock",
            "status",
            "approval_status",
            "created_at",
            "updated_at",
            "images",
            "prices",
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product list views.
    Only includes essential fields for better performance including basic pricing.
    """

    user = UserSimpleSerializer(read_only=True)
    category = CategorySimpleSerializer(read_only=True)
    prices = ProductPriceListSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "uuid",
            "user",
            "category",
            "name",
            "slug",
            "description",
            "image",
            "available_stock",
            "status",
            "approval_status",
            "created_at",
            "prices",
        ]
