from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from core.users.tests.factories import UserFactory
from ecommerce.tests.factories import CartFactory


class CartListAPITest(APITestCase):
    """Test suite for Cart List API endpoint."""

    fixtures = ["initial_data.json"]

    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("ecommerce:cart")
        # Create some cart items for this user
        self.cart_items = CartFactory.create_batch(3, user=self.user)

    def test_cart_list_authenticated(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3  # noqa: PLR2004
        for item in response.data["results"]:
            assert str(item["user"]["id"]) == str(self.user.id)

    def test_cart_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]
