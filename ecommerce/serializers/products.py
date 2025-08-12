from rest_framework import serializers

from ecommerce.models import Product
from ecommerce.models import ProductImage


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


class CreateProductSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new products.
    Handles product creation with main image field.
    """

    user = serializers.StringRelatedField(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "uuid",
            "user",
            "category",
            "category_name",
            "name",
            "description",
            "image",
            "available_stock",
            "status",
            "approval_status",
            "created_at",
        ]
        read_only_fields = [
            "uuid",
            "slug",
            "approval_status",
            "created_at",
        ]

    def validate_available_stock(self, value):
        """Validate that stock is non-negative."""
        if value < 0:
            msg = "Stock cannot be negative."
            raise serializers.ValidationError(msg)
        return value

    def create(self, validated_data):
        """
        Create product with user from request context.
        """
        # Set the user from request
        request = self.context.get("request")
        if request and request.user:
            validated_data["user"] = request.user

        # Create the product
        return Product.objects.create(**validated_data)


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
    Includes all product information with nested images.
    """

    user = serializers.StringRelatedField(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    images = ProductImageDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "uuid",
            "user",
            "category",
            "category_name",
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
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product list views.
    Only includes essential fields for better performance.
    """

    user = serializers.StringRelatedField(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "uuid",
            "user",
            "category",
            "category_name",
            "name",
            "slug",
            "description",
            "image",
            "available_stock",
            "status",
            "approval_status",
            "created_at",
        ]
