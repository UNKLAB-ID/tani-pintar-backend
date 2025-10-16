from rest_framework import serializers

from accounts.serializers import SimpleProfileDetailSerializer
from core.users.models import User
from core.users.serializers import UserDetailSerializer
from ecommerce.models import Cart
from ecommerce.models import Product
from ecommerce.serializers.products import ProductDetailSerializer
from ecommerce.serializers.products import ProductListSerializer


class CartUserProfileSerializer(serializers.ModelSerializer):
    """
    Simple user serializer with profile for cart items.
    """

    profile = SimpleProfileDetailSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "profile"]
        read_only_fields = fields


class CartListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing cart items.
    Read-only serializer with full product details and user profile.
    """

    product = ProductListSerializer(read_only=True)
    user = CartUserProfileSerializer(read_only=True)

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


class CartCreateSerializer(serializers.Serializer):
    """
    Serializer for creating cart items.
    """

    product_uuid = serializers.UUIDField()
    quantity = serializers.IntegerField()

    def validate_product_uuid(self, value):
        """
        Validate that the product exists and is active.
        """
        try:
            product = Product.objects.get(
                uuid=value,
                approval_status=Product.APPROVAL_APPROVED,
                status=Product.STATUS_ACTIVE,
            )
        except Product.DoesNotExist:
            msg = "Product with the given UUID does not exist or is inactive."
            raise serializers.ValidationError(msg)  # noqa: B904
        return product

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
        Create or update cart item with stock validation.
        """

        user = self.context["request"].user
        product = Product.objects.select_for_update().get(
            uuid=validated_data["product_uuid"].uuid,
        )
        quantity = validated_data["quantity"]

        if quantity > product.available_stock:
            available = product.available_stock
            msg = f"Quantity exceeds available stock ({available})."
            raise serializers.ValidationError({"quantity": msg})

        cart_item, created = Cart.objects.get_or_create(
            user=user,
            product=product,
            defaults={"quantity": quantity},
        )

        if not created:
            new_quantity = quantity
            if new_quantity > product.available_stock:
                available = product.available_stock
                msg = f"Total quantity exceeds available stock ({available})."
                raise serializers.ValidationError({"quantity": msg})
            cart_item.quantity = new_quantity
            cart_item.save()

        return cart_item


class CartDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for cart detail view.
    Read-only serializer with full product details and user profile.
    """

    product = ProductDetailSerializer(read_only=True)
    user = UserDetailSerializer(read_only=True)

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
