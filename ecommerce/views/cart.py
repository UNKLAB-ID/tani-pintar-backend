from rest_framework import serializers
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from ecommerce.models import Cart
from ecommerce.serializers.cart import CartSerializer


class CartListCreateView(ListCreateAPIView):
    """
    API view for listing and creating cart items.
    GET: List user's cart items.
    POST: Add item to cart.
    """

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return cart items for the current user."""
        return Cart.objects.filter(user=self.request.user).select_related(
            "user",
            "product",
        )

    def perform_create(self, serializer):
        """Set the user for the cart item."""
        # Check if item already exists
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        existing_item = Cart.objects.filter(
            user=self.request.user,
            product=product,
        ).first()

        if existing_item:
            # Update existing item quantity
            new_quantity = existing_item.quantity + quantity
            if new_quantity > product.available_stock:
                available = product.available_stock
                msg = f"Total quantity would exceed available stock ({available})."
                raise serializers.ValidationError({"quantity": msg})

            existing_item.quantity = new_quantity
            existing_item.save()
            # Return the existing item (this won't actually create a new one)
            serializer.instance = existing_item
        else:
            # Create new item
            serializer.save(user=self.request.user)


class CartDetailView(RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating and deleting cart items.
    GET: Retrieve cart item.
    PUT/PATCH: Update cart item.
    DELETE: Remove item from cart.
    """

    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return cart items for the current user."""
        return Cart.objects.filter(user=self.request.user).select_related(
            "user",
            "product",
        )
