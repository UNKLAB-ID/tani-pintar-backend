import uuid

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from ecommerce.tests.factories import ProductCategoryFactory
from ecommerce.tests.factories import ProductSubCategoryFactory


class SubCategoryListAPITest(APITestCase):
    def setUp(self):
        self.url = reverse("ecommerce:subcategory-list")
        self.active_category = ProductCategoryFactory(
            name="Electronics",
            is_active=True,
        )
        self.inactive_category = ProductCategoryFactory(
            name="Inactive",
            is_active=False,
        )

        self.active_subcategory = ProductSubCategoryFactory(
            name="Laptops",
            category=self.active_category,
            is_active=True,
        )
        self.inactive_subcategory = ProductSubCategoryFactory(
            name="Inactive Laptop",
            category=self.active_category,
            is_active=False,
        )

    def test_get_subcategory_list_success(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1  # Only active subcategories

    def test_subcategory_list_only_returns_active_subcategories(self):
        response = self.client.get(self.url)

        subcategory_names = [subcat["name"] for subcat in response.data]
        assert "Laptops" in subcategory_names
        assert "Inactive Laptop" not in subcategory_names

    def test_subcategory_list_response_structure(self):
        response = self.client.get(self.url)

        assert isinstance(response.data, list)
        assert len(response.data) >= 0

    def test_subcategory_list_item_structure(self):
        response = self.client.get(self.url)
        subcategory = response.data[0]

        expected_fields = {"id", "name", "slug", "category"}
        assert set(subcategory.keys()) == expected_fields

    def test_subcategory_list_includes_category_data(self):
        response = self.client.get(self.url)
        subcategory_data = response.data[0]

        assert subcategory_data["category"] is not None
        assert subcategory_data["category"]["name"] == "Electronics"
        assert subcategory_data["category"]["id"] == str(self.active_category.id)

    def test_subcategory_list_category_structure(self):
        response = self.client.get(self.url)
        category_data = response.data[0]["category"]

        expected_fields = {"id", "name", "slug"}
        assert set(category_data.keys()) == expected_fields

    def test_subcategory_list_includes_subcategories_with_inactive_category(self):
        ProductSubCategoryFactory(
            name="Subcategory of Inactive",
            category=self.inactive_category,
            is_active=True,
        )

        response = self.client.get(self.url)

        # Current implementation shows subcategories even if parent category is inactive
        # as long as the subcategory itself is active
        assert len(response.data) == 2  # noqa: PLR2004
        subcategory_names = [subcat["name"] for subcat in response.data]
        assert "Laptops" in subcategory_names
        assert "Subcategory of Inactive" in subcategory_names

    def test_subcategory_list_search_by_name(self):
        ProductSubCategoryFactory(
            name="Gaming Laptops",
            category=self.active_category,
            is_active=True,
        )

        response = self.client.get(self.url, {"search": "Gaming"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Gaming Laptops"

    def test_subcategory_list_search_by_description(self):
        ProductSubCategoryFactory(
            name="Special Product",
            description="High-performance gaming computers",
            category=self.active_category,
            is_active=True,
        )

        response = self.client.get(self.url, {"search": "gaming"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Special Product"

    def test_subcategory_list_search_by_category_name(self):
        response = self.client.get(self.url, {"search": "Electronics"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["category"]["name"] == "Electronics"

    def test_subcategory_list_filter_by_category(self):
        other_category = ProductCategoryFactory(name="Fashion", is_active=True)
        ProductSubCategoryFactory(
            name="Shoes",
            category=other_category,
            is_active=True,
        )

        response = self.client.get(
            self.url,
            {"category": str(self.active_category.id)},
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Laptops"

    def test_subcategory_list_filter_by_is_active(self):
        response = self.client.get(self.url, {"is_active": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Laptops"

    def test_subcategory_list_ordering_by_name(self):
        ProductSubCategoryFactory(
            name="Zebra Product",
            category=self.active_category,
            is_active=True,
        )

        response = self.client.get(self.url, {"ordering": "name"})

        assert response.status_code == status.HTTP_200_OK
        subcategory_names = [subcat["name"] for subcat in response.data]
        assert subcategory_names == sorted(subcategory_names)

    def test_subcategory_list_ordering_by_created_at_desc(self):
        response = self.client.get(self.url, {"ordering": "-created_at"})

        assert response.status_code == status.HTTP_200_OK
        # Should return results without error


class SubCategoryDetailAPITest(APITestCase):
    def setUp(self):
        self.active_category = ProductCategoryFactory(
            name="Electronics",
            is_active=True,
        )
        self.active_subcategory = ProductSubCategoryFactory(
            name="Laptops",
            description="Laptop computers",
            category=self.active_category,
            is_active=True,
        )
        self.inactive_subcategory = ProductSubCategoryFactory(
            name="Inactive Subcategory",
            category=self.active_category,
            is_active=False,
        )
        self.url = reverse(
            "ecommerce:subcategory-detail",
            kwargs={"slug": self.active_subcategory.slug},
        )

    def test_get_subcategory_detail_success(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Laptops"
        assert response.data["id"] == str(self.active_subcategory.id)

    def test_subcategory_detail_response_structure(self):
        response = self.client.get(self.url)

        expected_fields = {"id", "name", "category", "slug"}
        assert set(response.data.keys()) == expected_fields

    def test_subcategory_detail_includes_category_data(self):
        response = self.client.get(self.url)

        assert response.data["category"] is not None
        assert response.data["category"]["name"] == "Electronics"
        assert response.data["category"]["id"] == str(self.active_category.id)

    def test_subcategory_detail_category_structure(self):
        response = self.client.get(self.url)
        category_data = response.data["category"]

        expected_fields = {"id", "name", "slug"}
        assert set(category_data.keys()) == expected_fields
        assert category_data["slug"] == self.active_category.slug

    def test_subcategory_detail_not_found_for_inactive_subcategory(self):
        url = reverse(
            "ecommerce:subcategory-detail",
            kwargs={"slug": self.inactive_subcategory.slug},
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_subcategory_detail_not_found_for_nonexistent_slug(self):
        url = reverse(
            "ecommerce:subcategory-detail",
            kwargs={"slug": "nonexistent-subcategory"},
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_subcategory_detail_slug_field_present(self):
        response = self.client.get(self.url)

        assert response.data["slug"] == self.active_subcategory.slug

    def test_subcategory_detail_with_inactive_parent_category(self):
        inactive_category = ProductCategoryFactory(name="Inactive", is_active=False)
        subcategory_with_inactive_parent = ProductSubCategoryFactory(
            name="Test Subcategory",
            category=inactive_category,
            is_active=True,
        )

        url = reverse(
            "ecommerce:subcategory-detail",
            kwargs={"slug": subcategory_with_inactive_parent.slug},
        )
        response = self.client.get(url)

        # Should return the subcategory but with category data showing inactive parent
        assert response.status_code == status.HTTP_200_OK
        assert (
            response.data["category"] is None
        )  # Inactive parent category is filtered out


@pytest.mark.django_db
class SubCategoryAPIPermissionTest:
    def test_subcategory_list_allows_anonymous_access(self):
        url = reverse("ecommerce:subcategory-list")

        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_subcategory_detail_allows_anonymous_access(self):
        category = ProductCategoryFactory(is_active=True)
        subcategory = ProductSubCategoryFactory(category=category, is_active=True)
        url = reverse(
            "ecommerce:subcategory-detail",
            kwargs={"slug": subcategory.slug},
        )

        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class SubCategoryAPIEdgeCaseTest:
    def test_subcategory_list_with_no_subcategories(self):
        url = reverse("ecommerce:subcategory-list")

        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_subcategory_list_search_no_results(self):
        category = ProductCategoryFactory(name="Electronics", is_active=True)
        ProductSubCategoryFactory(
            name="Laptops",
            category=category,
            is_active=True,
        )
        url = reverse("ecommerce:subcategory-list")

        client = APIClient()

        response = client.get(url, {"search": "NonexistentSubcategory"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_subcategory_list_filter_by_nonexistent_category(self):
        url = reverse("ecommerce:subcategory-list")

        client = APIClient()

        response = client.get(url, {"category": str(uuid.uuid4())})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_subcategory_detail_with_special_characters_in_slug(self):
        category = ProductCategoryFactory(name="Electronics", is_active=True)
        subcategory = ProductSubCategoryFactory(
            name="Gaming & Entertainment",
            category=category,
            is_active=True,
        )

        url = reverse(
            "ecommerce:subcategory-detail",
            kwargs={"slug": subcategory.slug},
        )

        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Gaming & Entertainment"


@pytest.mark.django_db
class SubCategoryAPIIntegrationTest:
    def test_subcategory_list_with_multiple_categories(self):
        # Create multiple categories with subcategories
        electronics = ProductCategoryFactory(name="Electronics", is_active=True)
        fashion = ProductCategoryFactory(name="Fashion", is_active=True)

        ProductSubCategoryFactory(
            name="Laptops",
            category=electronics,
            is_active=True,
        )
        ProductSubCategoryFactory(
            name="Phones",
            category=electronics,
            is_active=True,
        )
        ProductSubCategoryFactory(
            name="Shoes",
            category=fashion,
            is_active=True,
        )

        url = reverse("ecommerce:subcategory-list")

        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3  # noqa: PLR2004

        subcategory_names = [subcat["name"] for subcat in response.data]
        assert "Laptops" in subcategory_names
        assert "Phones" in subcategory_names
        assert "Shoes" in subcategory_names

    def test_subcategory_filtering_and_search_combined(self):
        electronics = ProductCategoryFactory(name="Electronics", is_active=True)
        fashion = ProductCategoryFactory(name="Fashion", is_active=True)

        ProductSubCategoryFactory(
            name="Gaming Laptops",
            category=electronics,
            is_active=True,
        )
        ProductSubCategoryFactory(
            name="Gaming Shoes",
            category=fashion,
            is_active=True,
        )

        url = reverse("ecommerce:subcategory-list")

        client = APIClient()

        # Filter by category and search for "Gaming"
        response = client.get(
            url,
            {
                "category": str(electronics.id),
                "search": "Gaming",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Gaming Laptops"
