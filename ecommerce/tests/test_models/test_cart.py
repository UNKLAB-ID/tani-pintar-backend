from django.test import TestCase

from ecommerce.models import Cart
from ecommerce.tests.factories import CartFactory


class TestCartFactory(TestCase):
    fixtures = ["initial_data.json"]

    def test_cart_factory_creates_valid_cart(self):
        cart = CartFactory()
        assert isinstance(cart, Cart)
        assert cart.user is not None
        assert cart.product is not None
        assert cart.quantity > 0
        assert cart.pk is not None
        assert (
            str(cart)
            == f"{cart.product.name} ({cart.quantity}) in {cart.user.username}'s cart"
        )
