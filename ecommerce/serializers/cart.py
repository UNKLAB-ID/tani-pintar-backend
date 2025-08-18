from rest_framework import serializers

from ecommerce.models import Cart
from ecommerce.models import Product
from ecommerce.serializers.products import ProductListSerializer


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for Cart model.
    Includes product details for cart items.
    """

    product = ProductListSerializer(read_only=True)
    product_uuid = serializers.UUIDField(write_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "user",
            "product",
            "product_uuid",
            "quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

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

    def update(self, instance, validated_data):
        """
        Update cart item, handling product changes if needed.
        """
        if "product_uuid" in validated_data:
            product_uuid = validated_data.pop("product_uuid")
            product = Product.objects.get(uuid=product_uuid)
            validated_data["product"] = product

        # Check stock availability for new quantity
        new_quantity = validated_data.get("quantity", instance.quantity)
        product = validated_data.get("product", instance.product)

        if new_quantity > product.available_stock:
            msg = f"Quantity exceeds available stock ({product.available_stock})."
            raise serializers.ValidationError({"quantity": msg})

        return super().update(instance, validated_data)
