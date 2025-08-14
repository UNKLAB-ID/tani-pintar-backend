from rest_framework import serializers

from ecommerce.models import Cart
from ecommerce.models import CartItem
from ecommerce.models import Product


class SimpleProductSerializer(serializers.ModelSerializer):
    """
    Simple serializer for Product model.
    Returns basic product information needed for cart display.
    """

    class Meta:
        model = Product
        fields = [
            "uuid",
            "name",
            "image",
            "available_stock",
            "status",
            "approval_status",
        ]
        read_only_fields = fields


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem model.
    Includes product details and allows CRUD operations on quantity.
    """

    product = SimpleProductSerializer(read_only=True)
    product_uuid = serializers.UUIDField(write_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_uuid",
            "quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

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
        Validate that quantity is positive and doesn't exceed available stock.
        """
        if value <= 0:
            msg = "Quantity must be greater than 0."
            raise serializers.ValidationError(msg)

        # Check stock availability during update
        if self.instance:
            product = self.instance.product
            if value > product.available_stock:
                msg = f"Quantity exceeds available stock ({product.available_stock})."
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
            msg = f"Quantity exceeds available stock ({product.available_stock})."
            raise serializers.ValidationError({"quantity": msg})

        validated_data["product"] = product
        return super().create(validated_data)


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for Cart model.
    Includes all cart items and calculated totals.
    """

    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "items",
            "total_items",
            "items_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CartItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating cart items.
    Simplified version for API endpoints.
    """

    product_uuid = serializers.UUIDField()

    class Meta:
        model = CartItem
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
