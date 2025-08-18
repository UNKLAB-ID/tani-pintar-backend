from rest_framework import serializers

from ecommerce.models import Cart
from ecommerce.models import Product
from ecommerce.serializers.products import ProductDetailSerializer
from ecommerce.serializers.products import ProductListSerializer


class CartListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing cart items.
    Read-only serializer with full product details.
    """

    product = ProductListSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "product",
            "quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CartCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating cart items.
    """

    product_uuid = serializers.UUIDField()

    class Meta:
        model = Cart
        fields = ["product_uuid", "quantity"]

    def validate_product_uuid(self, value):
        """
        Validate that the product exists and is active/approved.
        """
        try:
            product = Product.objects.get(uuid=value)
        except Product.DoesNotExist as exc:
            msg = "Product with this UUID does not exist."
            raise serializers.ValidationError(msg) from exc

        if product.status != Product.STATUS_ACTIVE:
            msg = "Product is not active."
            raise serializers.ValidationError(msg)

        if product.approval_status != Product.APPROVAL_APPROVED:
            msg = "Product is not approved."
            raise serializers.ValidationError(msg)

        return value

    def validate_quantity(self, value):
        """
        Validate that quantity is positive.
        """
        if value <= 0:
            msg = "Quantity must be greater than 0."
            raise serializers.ValidationError(msg)

        return value

    def create(self, validated_data):
        """
        Create a new cart item.
        """
        product_uuid = validated_data.pop("product_uuid")
        product = Product.objects.get(uuid=product_uuid)

        # Check stock availability
        if validated_data["quantity"] > product.available_stock:
            available = product.available_stock
            msg = f"Quantity exceeds available stock ({available})."
            raise serializers.ValidationError({"quantity": msg})

        validated_data["product"] = product
        return super().create(validated_data)


class CartDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for cart detail view.
    Read-only serializer with full product details.
    """

    product = ProductDetailSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "product",
            "quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CartUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating cart items.
    """

    class Meta:
        model = Cart
        fields = ["quantity"]

    def validate_quantity(self, value):
        """
        Validate that quantity is positive and doesn't exceed available stock.
        """
        if value <= 0:
            msg = "Quantity must be greater than 0."
            raise serializers.ValidationError(msg)

        return value

    def update(self, instance, validated_data):
        """
        Update cart item quantity with stock validation.
        """
        new_quantity = validated_data.get("quantity", instance.quantity)

        if new_quantity > instance.product.available_stock:
            available = instance.product.available_stock
            msg = f"Quantity exceeds available stock ({available})."
            raise serializers.ValidationError({"quantity": msg})

        return super().update(instance, validated_data)
