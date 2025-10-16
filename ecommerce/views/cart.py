from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ecommerce.models import Cart
from ecommerce.paginations import CartCursorPagination
from ecommerce.serializers.cart import CartCreateSerializer
from ecommerce.serializers.cart import CartDetailSerializer
from ecommerce.serializers.cart import CartListSerializer
from ecommerce.serializers.cart import CartUpdateSerializer


class CartListCreateView(ListCreateAPIView):
    """
    API view for listing and creating cart items.
    GET: List user's cart items with cursor pagination.
    POST: Add item to cart.
    """

    permission_classes = [IsAuthenticated]
    pagination_class = CartCursorPagination

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.request.method == "POST":
            return CartCreateSerializer
        return CartListSerializer

    def get_queryset(self):
        """Return cart items for the current user."""
        return Cart.objects.filter(user=self.request.user).select_related(
            "user",
            "product",
        )

    def create(self, request, *args, **kwargs):
        """
        Override create to handle duplicate cart items.
        If item already in cart, increment quantity instead of creating new entry.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart = serializer.save()

        return Response(
            CartDetailSerializer(cart, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class CartItemView(RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating and deleting cart items.
    GET: Retrieve cart item.
    PUT/PATCH: Update cart item.
    DELETE: Remove item from cart.
    """

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.request.method in ["PUT", "PATCH"]:
            return CartUpdateSerializer
        return CartDetailSerializer

    def get_queryset(self):
        """Return cart items for the current user."""
        return Cart.objects.filter(user=self.request.user).select_related(
            "user",
            "product",
        )
