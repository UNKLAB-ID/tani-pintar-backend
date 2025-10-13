import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from core.users.tests.factories import UserFactory
from ecommerce.models import Product
from ecommerce.models import ProductPrice
from ecommerce.tests.factories import ProductCategoryFactory
from ecommerce.tests.factories import ProductFactory
from ecommerce.tests.factories import ProductImageFactory
from ecommerce.tests.factories import UnitOfMeasureFactory
from vendors.tests.factories import VendorFactory


class ProductListAPITest(APITestCase):
    """Test suite for Product List API endpoint."""

    fixtures = ["initial_data.json"]

    def setUp(self):
        """Set up test data for product list tests."""
        self.url = reverse("ecommerce:product-list-create")
        self.category = ProductCategoryFactory(name="Electronics", is_active=True)

        # Create approved products visible to all
        self.approved_product1 = ProductFactory(
            name="Laptop",
            category=self.category,
            status=Product.STATUS_ACTIVE,
            approval_status=Product.APPROVAL_APPROVED,
            prices=0,
            images=0,
        )
        self.approved_product2 = ProductFactory(
            name="Phone",
            category=self.category,
            status=Product.STATUS_ACTIVE,
            approval_status=Product.APPROVAL_APPROVED,
            prices=0,
            images=0,
        )

        # Create user and their products with different statuses
        self.user = UserFactory()
        self.vendor = VendorFactory(user=self.user)

        self.user_pending_product = ProductFactory(
            name="User Pending Product",
            category=self.category,
            user=self.user,
            status=Product.STATUS_DRAFT,
            approval_status=Product.APPROVAL_PENDING,
            prices=0,
            images=0,
        )

    def test_get_product_list_success(self):
        """Test successful product list retrieval."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert isinstance(response.data["results"], list)

    def test_list_returns_only_approved_products_for_anonymous(self):
        """Test anonymous users only see approved products."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        product_names = [p["name"] for p in response.data["results"]]
        assert "Laptop" in product_names
        assert "Phone" in product_names
        assert "User Pending Product" not in product_names

    def test_authenticated_users_see_approved_plus_own_products(self):
        """Test authenticated users see approved products + their own."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        product_names = [p["name"] for p in response.data["results"]]
        assert "Laptop" in product_names
        assert "Phone" in product_names
        assert "User Pending Product" in product_names

    def test_product_list_response_structure(self):
        """Test product list response has pagination structure."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        expected_keys = {"next", "previous", "results"}
        assert set(response.data.keys()) == expected_keys

    def test_product_list_item_structure(self):
        """Test individual product item has correct structure."""
        response = self.client.get(self.url)
        product = response.data["results"][0]

        expected_fields = {
            "uuid",
            "user",
            "category",
            "name",
            "slug",
            "description",
            "image",
            "available_stock",
            "status",
            "approval_status",
            "created_at",
            "prices",
        }
        assert set(product.keys()) == expected_fields

    def test_filter_by_category(self):
        """Test filtering products by category."""
        other_category = ProductCategoryFactory(name="Books", is_active=True)
        ProductFactory(
            name="Novel",
            category=other_category,
            approval_status=Product.APPROVAL_APPROVED,
            prices=0,
            images=0,
        )

        response = self.client.get(self.url, {"category": str(self.category.id)})

        assert response.status_code == status.HTTP_200_OK
        for product in response.data["results"]:
            assert product["category"]["id"] == str(self.category.id)

    def test_filter_by_status(self):
        """Test filtering products by status."""
        ProductFactory(
            name="Draft Product",
            category=self.category,
            status=Product.STATUS_DRAFT,
            approval_status=Product.APPROVAL_APPROVED,
            prices=0,
            images=0,
        )

        response = self.client.get(self.url, {"status": Product.STATUS_ACTIVE})

        assert response.status_code == status.HTTP_200_OK
        for product in response.data["results"]:
            assert product["status"] == Product.STATUS_ACTIVE

    def test_filter_by_approval_status(self):
        """Test filtering products by approval status."""
        response = self.client.get(
            self.url,
            {"approval_status": Product.APPROVAL_APPROVED},
        )

        assert response.status_code == status.HTTP_200_OK
        for product in response.data["results"]:
            assert product["approval_status"] == Product.APPROVAL_APPROVED

    def test_filter_by_user(self):
        """Test filtering products by user."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url, {"user": str(self.user.id)})

        assert response.status_code == status.HTTP_200_OK
        for product in response.data["results"]:
            assert product["user"]["id"] == self.user.id

    def test_search_by_name(self):
        """Test searching products by name."""
        response = self.client.get(self.url, {"search": "Laptop"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1
        product_names = [p["name"] for p in response.data["results"]]
        assert any("Laptop" in name for name in product_names)

    def test_search_by_description(self):
        """Test searching products by description."""
        ProductFactory(
            name="Special Item",
            description="Unique description keyword test",
            category=self.category,
            approval_status=Product.APPROVAL_APPROVED,
            prices=0,
            images=0,
        )

        response = self.client.get(self.url, {"search": "Unique"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1

    def test_combined_filters(self):
        """Test using multiple filters together."""
        response = self.client.get(
            self.url,
            {
                "category": str(self.category.id),
                "status": Product.STATUS_ACTIVE,
                "approval_status": Product.APPROVAL_APPROVED,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        for product in response.data["results"]:
            assert product["category"]["id"] == str(self.category.id)
            assert product["status"] == Product.STATUS_ACTIVE
            assert product["approval_status"] == Product.APPROVAL_APPROVED

    def test_pagination_structure(self):
        """Test cursor pagination is present."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data

    def test_pagination_with_multiple_products(self):
        """Test pagination works with multiple products."""
        # Create additional products
        for i in range(10):
            ProductFactory(
                name=f"Product {i}",
                category=self.category,
                approval_status=Product.APPROVAL_APPROVED,
                prices=0,
                images=0,
            )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) > 0

    def test_anonymous_users_can_access_list(self):
        """Test anonymous users have read access to product list."""
        client = APIClient()
        response = client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_authenticated_non_vendor_can_access_list(self):
        """Test authenticated non-vendors can access product list."""
        user = UserFactory()
        self.client.force_authenticate(user=user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK

    def test_empty_product_list(self):
        """Test empty product list returns successfully."""
        Product.objects.all().delete()
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0

    def test_list_with_no_approved_products(self):
        """Test list when no approved products exist (anonymous user)."""
        Product.objects.all().delete()
        ProductFactory(
            name="Pending",
            approval_status=Product.APPROVAL_PENDING,
            prices=0,
            images=0,
        )

        client = APIClient()
        response = client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0


class ProductDetailAPITest(APITestCase):
    """Test suite for Product Detail API endpoint."""

    fixtures = ["initial_data.json"]

    def setUp(self):
        """Set up test data for product detail tests."""
        self.category = ProductCategoryFactory(name="Electronics", is_active=True)
        self.user = UserFactory()
        self.vendor = VendorFactory(user=self.user)

        # Create approved product with images and prices
        self.approved_product = ProductFactory(
            name="Laptop",
            category=self.category,
            user=self.user,
            status=Product.STATUS_ACTIVE,
            approval_status=Product.APPROVAL_APPROVED,
            prices=0,
            images=0,
        )

        # Add images and prices manually to avoid factory issues
        self.image1 = ProductImageFactory(
            product=self.approved_product,
            caption="Front view",
        )
        self.image2 = ProductImageFactory(
            product=self.approved_product,
            caption="Side view",
        )

        self.uom1 = UnitOfMeasureFactory(name="piece")
        self.uom2 = UnitOfMeasureFactory(name="box")
        self.price1 = ProductPrice.objects.create(
            product=self.approved_product,
            unit_of_measure=self.uom1,
            price=1000.00,
        )
        self.price2 = ProductPrice.objects.create(
            product=self.approved_product,
            unit_of_measure=self.uom2,
            price=5000.00,
        )

        # Create pending product
        self.pending_product = ProductFactory(
            name="Pending Product",
            category=self.category,
            user=self.user,
            approval_status=Product.APPROVAL_PENDING,
            prices=0,
            images=0,
        )

        self.url = reverse(
            "ecommerce:product-detail",
            kwargs={"pk": self.approved_product.uuid},
        )

    def test_get_product_detail_success(self):
        """Test successful product detail retrieval by UUID."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Laptop"
        assert response.data["uuid"] == str(self.approved_product.uuid)

    def test_detail_response_includes_all_fields(self):
        """Test detail response includes user, category, images, prices."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "user" in response.data
        assert "category" in response.data
        assert "images" in response.data
        assert "prices" in response.data

    def test_detail_response_structure(self):
        """Test product detail has correct field structure."""
        response = self.client.get(self.url)

        expected_fields = {
            "uuid",
            "user",
            "category",
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
            "prices",
        }
        assert set(response.data.keys()) == expected_fields

    def test_product_not_found_returns_404(self):
        """Test accessing non-existent product returns 404."""
        import uuid

        url = reverse(
            "ecommerce:product-detail",
            kwargs={"pk": uuid.uuid4()},
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_anonymous_users_can_view_approved_products(self):
        """Test anonymous users can view approved products."""
        client = APIClient()
        response = client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Laptop"

    def test_anonymous_users_cannot_view_pending_products(self):
        """Test anonymous users cannot view pending products."""
        url = reverse(
            "ecommerce:product-detail",
            kwargs={"pk": self.pending_product.uuid},
        )
        client = APIClient()
        response = client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_authenticated_users_can_view_own_products(self):
        """Test users can view their own products regardless of status."""
        self.client.force_authenticate(user=self.user)
        url = reverse(
            "ecommerce:product-detail",
            kwargs={"pk": self.pending_product.uuid},
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Pending Product"

    def test_authenticated_users_cannot_view_others_unapproved(self):
        """Test users cannot view other users' unapproved products."""
        other_user = UserFactory()
        self.client.force_authenticate(user=other_user)

        url = reverse(
            "ecommerce:product-detail",
            kwargs={"pk": self.pending_product.uuid},
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_product_includes_related_images(self):
        """Test product detail includes related images."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["images"]) == 2  # noqa: PLR2004
        image_captions = [img["caption"] for img in response.data["images"]]
        assert "Front view" in image_captions
        assert "Side view" in image_captions

    def test_product_includes_related_prices(self):
        """Test product detail includes prices with unit of measure."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["prices"]) == 2  # noqa: PLR2004

        # Check price structure
        price_data = response.data["prices"][0]
        assert "id" in price_data
        assert "price" in price_data
        assert "unit_of_measure" in price_data

    def test_user_data_serialized_correctly(self):
        """Test user data is properly serialized."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        user_data = response.data["user"]
        assert "id" in user_data
        assert "username" in user_data
        assert user_data["id"] == self.user.id

    def test_category_data_serialized_correctly(self):
        """Test category data is properly serialized."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        category_data = response.data["category"]
        assert "id" in category_data
        assert "name" in category_data
        assert category_data["name"] == "Electronics"

    def test_images_properly_structured(self):
        """Test images array has proper structure."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        for image in response.data["images"]:
            expected_fields = {"id", "image", "caption", "created_at"}
            assert set(image.keys()) == expected_fields

    def test_prices_with_uom_properly_structured(self):
        """Test prices include unit of measure details."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        for price in response.data["prices"]:
            assert "unit_of_measure" in price
            uom = price["unit_of_measure"]
            assert "id" in uom
            assert "name" in uom

    def test_product_with_no_images(self):
        """Test product detail works with no images."""
        product_no_images = ProductFactory(
            name="No Images Product",
            category=self.category,
            approval_status=Product.APPROVAL_APPROVED,
            prices=0,
            images=0,
        )

        url = reverse(
            "ecommerce:product-detail",
            kwargs={"pk": product_no_images.uuid},
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["images"]) == 0

    def test_product_with_no_prices(self):
        """Test product detail works with no prices."""
        product_no_prices = ProductFactory(
            name="No Prices Product",
            category=self.category,
            approval_status=Product.APPROVAL_APPROVED,
            prices=0,
            images=0,
        )

        url = reverse(
            "ecommerce:product-detail",
            kwargs={"pk": product_no_prices.uuid},
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["prices"]) == 0

    def test_product_with_invalid_uuid_format(self):
        """Test accessing product with invalid UUID format."""
        # This will likely result in a 404 or URL resolution error
        # depending on URL configuration
        url = "/ecommerce/products/invalid-uuid/"
        response = self.client.get(url)

        # Should return 404 since invalid UUID won't match any product
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class ProductAPIPermissionTest:
    """Test suite for product API permissions."""

    fixtures = ["initial_data.json"]

    def test_list_allows_anonymous_access(self):
        """Test product list allows anonymous access."""
        url = reverse("ecommerce:product-list-create")
        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_detail_allows_anonymous_access_for_approved(self):
        """Test product detail allows anonymous access for approved products."""
        product = ProductFactory(
            approval_status=Product.APPROVAL_APPROVED,
            prices=0,
            images=0,
        )
        url = reverse("ecommerce:product-detail", kwargs={"pk": product.uuid})
        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class ProductAPIEdgeCaseTest:
    """Test suite for product API edge cases."""

    fixtures = ["initial_data.json"]

    def test_list_with_deleted_category(self):
        """Test product list when category is deleted."""
        category = ProductCategoryFactory(is_active=True)
        product = ProductFactory(
            category=category,
            approval_status=Product.APPROVAL_APPROVED,
            prices=0,
            images=0,
        )
        category.delete()

        # Product should be deleted due to cascade
        url = reverse("ecommerce:product-list-create")
        client = APIClient()
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        product_uuids = [p["uuid"] for p in response.data["results"]]
        assert str(product.uuid) not in product_uuids

    def test_list_search_no_results(self):
        """Test product list search with no matching results."""
        ProductFactory(
            name="Laptop",
            approval_status=Product.APPROVAL_APPROVED,
            prices=0,
            images=0,
        )
        url = reverse("ecommerce:product-list-create")
        client = APIClient()

        response = client.get(url, {"search": "NonexistentProductName"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0

    def test_detail_product_slug_is_present(self):
        """Test product detail includes slug field."""
        product = ProductFactory(
            approval_status=Product.APPROVAL_APPROVED,
            prices=0,
            images=0,
        )
        url = reverse("ecommerce:product-detail", kwargs={"pk": product.uuid})
        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "slug" in response.data
        assert response.data["slug"] == product.slug
