from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ecommerce.models import Cart
from ecommerce.models import CartItem
from ecommerce.models import Product
from ecommerce.serializers import CartItemCreateSerializer
from ecommerce.serializers import CartItemSerializer
from ecommerce.serializers import CartSerializer


class CartListView(APIView):
    """
    API view for managing user's cart.
    GET: Retrieve user's cart (create if doesn't exist).
    DELETE: Clear all items from cart.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get or create user's cart."""
        user = request.user

        # Admin can see all carts
        if user.is_staff or user.is_superuser:
            carts = Cart.objects.all().prefetch_related("items__product")
            serializer = CartSerializer(carts, many=True)
            return Response(serializer.data)

        # Regular user gets their own cart
        cart, created = Cart.objects.get_or_create(user=user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def delete(self, request):
        """Clear all items from user's cart."""
        user = request.user

        if user.is_staff or user.is_superuser:
            return Response(
                {"detail": "Admin users cannot modify carts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        cart, created = Cart.objects.get_or_create(user=user)
        cart.items.all().delete()

        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartDetailView(APIView):
    """
    API view for retrieving specific cart.
    Only for admin users to view any cart.
    Regular users should use CartListView.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """Get specific cart by ID."""
        user = request.user

        if not (user.is_staff or user.is_superuser):
            return Response(
                {"detail": "Only admin users can access specific carts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        cart = get_object_or_404(Cart, pk=pk)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemListCreateView(APIView):
    """
    API view for managing cart items.
    GET: List user's cart items.
    POST: Add item to cart.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """List user's cart items."""
        user = request.user

        if user.is_staff or user.is_superuser:
            # Admin can see all cart items
            cart_items = CartItem.objects.all().select_related(
                "cart__user",
                "product",
            )
        else:
            # Regular user sees their own cart items
            cart_items = CartItem.objects.filter(cart__user=user).select_related(
                "cart__user",
                "product",
            )

        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):  # noqa: PLR0911
        """Add item to user's cart."""
        user = request.user

        if user.is_staff or user.is_superuser:
            return Response(
                {"detail": "Admin users cannot modify cart items."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CartItemCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Get or create user's cart
        cart, created = Cart.objects.get_or_create(user=user)

        product_uuid = serializer.validated_data["product_uuid"]
        quantity = serializer.validated_data["quantity"]

        # Get the product
        try:
            product = Product.objects.get(uuid=product_uuid)
        except Product.DoesNotExist:
            return Response(
                {"product_uuid": ["Product with this UUID does not exist."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check product status
        if product.status != Product.STATUS_ACTIVE:
            return Response(
                {"product_uuid": ["Product is not active."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if product.approval_status != Product.APPROVAL_APPROVED:
            return Response(
                {"product_uuid": ["Product is not approved."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check stock availability
        if quantity > product.available_stock:
            available = product.available_stock
            msg = f"Quantity exceeds available stock ({available})."
            return Response(
                {"quantity": [msg]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if item already exists in cart
        existing_item = CartItem.objects.filter(cart=cart, product=product).first()
        if existing_item:
            # Update existing item
            new_quantity = existing_item.quantity + quantity
            if new_quantity > product.available_stock:
                available = product.available_stock
                msg = f"Total quantity would exceed available stock ({available})."
                return Response(
                    {"quantity": [msg]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            existing_item.quantity = new_quantity
            existing_item.save()

            response_serializer = CartItemSerializer(existing_item)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        # Create new cart item
        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity,
        )

        response_serializer = CartItemSerializer(cart_item)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    """
    API view for managing individual cart items.
    GET: Retrieve cart item.
    PUT/PATCH: Update cart item quantity.
    DELETE: Remove item from cart.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """Get cart item with permission check."""
        try:
            cart_item = CartItem.objects.select_related(
                "cart__user",
                "product",
            ).get(pk=pk)
        except CartItem.DoesNotExist:
            return None

        # Check permissions
        if not (user.is_staff or user.is_superuser) and cart_item.cart.user != user:
            return None

        return cart_item

    def get(self, request, pk):
        """Retrieve specific cart item."""
        cart_item = self.get_object(pk, request.user)
        if not cart_item:
            return Response(
                {"detail": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)

    def put(self, request, pk):
        """Update cart item quantity."""
        return self._update_item(request, pk, partial=False)

    def patch(self, request, pk):
        """Partially update cart item quantity."""
        return self._update_item(request, pk, partial=True)

    def _update_item(self, request, pk, partial=False):  # noqa: FBT002
        """Helper method for updating cart item."""
        user = request.user

        if user.is_staff or user.is_superuser:
            return Response(
                {"detail": "Admin users cannot modify cart items."},
                status=status.HTTP_403_FORBIDDEN,
            )

        cart_item = self.get_object(pk, user)
        if not cart_item:
            return Response(
                {"detail": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CartItemCreateSerializer(
            data=request.data,
            partial=partial,
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Validate quantity against stock
        new_quantity = serializer.validated_data.get("quantity", cart_item.quantity)
        if new_quantity > cart_item.product.available_stock:
            available = cart_item.product.available_stock
            msg = f"Quantity exceeds available stock ({available})."
            return Response(
                {"quantity": [msg]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update quantity
        cart_item.quantity = new_quantity
        cart_item.save()

        response_serializer = CartItemSerializer(cart_item)
        return Response(response_serializer.data)

    def delete(self, request, pk):
        """Remove item from cart."""
        user = request.user

        if user.is_staff or user.is_superuser:
            return Response(
                {"detail": "Admin users cannot modify cart items."},
                status=status.HTTP_403_FORBIDDEN,
            )

        cart_item = self.get_object(pk, user)
        if not cart_item:
            return Response(
                {"detail": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
