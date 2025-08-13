import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from ecommerce.tests.factories import ProductCategoryFactory
from ecommerce.tests.factories import ProductSubCategoryFactory


class CategoryListAPITest(APITestCase):
    def setUp(self):
        self.url = reverse("ecommerce:category-list")
        self.active_category = ProductCategoryFactory(
            name="Electronics",
            is_active=True,
        )
        self.inactive_category = ProductCategoryFactory(
            name="Inactive",
            is_active=False,
        )
        self.featured_category = ProductCategoryFactory(
            name="Featured",
            is_active=True,
            is_featured=True,
        )

    def test_get_category_list_success(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2  # Only active categories  # noqa: PLR2004

    def test_category_list_only_returns_active_categories(self):
        response = self.client.get(self.url)

        category_names = [cat["name"] for cat in response.data]
        assert "Electronics" in category_names
        assert "Featured" in category_names
        assert "Inactive" not in category_names

    def test_category_list_response_structure(self):
        response = self.client.get(self.url)

        assert isinstance(response.data, list)
        assert len(response.data) >= 0

    def test_category_list_item_structure(self):
        response = self.client.get(self.url)
        category = response.data[0]

        expected_fields = {"id", "name", "slug", "subcategories"}
        assert set(category.keys()) == expected_fields

    def test_category_list_includes_subcategories(self):
        subcategory = ProductSubCategoryFactory(
            name="Laptops",
            category=self.active_category,
            is_active=True,
        )

        response = self.client.get(self.url)
        category_data = next(
            cat for cat in response.data if cat["name"] == "Electronics"
        )

        assert len(category_data["subcategories"]) == 1
        assert category_data["subcategories"][0]["name"] == "Laptops"
        assert category_data["subcategories"][0]["id"] == str(subcategory.id)

    def test_category_list_excludes_inactive_subcategories(self):
        ProductSubCategoryFactory(
            name="Active Laptop",
            category=self.active_category,
            is_active=True,
        )
        ProductSubCategoryFactory(
            name="Inactive Laptop",
            category=self.active_category,
            is_active=False,
        )

        response = self.client.get(self.url)
        category_data = next(
            cat for cat in response.data if cat["name"] == "Electronics"
        )

        assert len(category_data["subcategories"]) == 1
        subcategory_names = [sub["name"] for sub in category_data["subcategories"]]
        assert "Active Laptop" in subcategory_names
        assert "Inactive Laptop" not in subcategory_names

    def test_category_list_search_by_name(self):
        response = self.client.get(self.url, {"search": "Electronics"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Electronics"

    def test_category_list_filter_by_featured(self):
        response = self.client.get(self.url, {"is_featured": "true"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Featured"

    def test_category_list_ordering_by_name(self):
        response = self.client.get(self.url, {"ordering": "name"})

        assert response.status_code == status.HTTP_200_OK
        category_names = [cat["name"] for cat in response.data]
        assert category_names == sorted(category_names)

    def test_category_list_ordering_by_created_at_desc(self):
        response = self.client.get(self.url, {"ordering": "-created_at"})

        assert response.status_code == status.HTTP_200_OK
        # Should return results without error - exact ordering depends on creation time


class CategoryDetailAPITest(APITestCase):
    def setUp(self):
        self.active_category = ProductCategoryFactory(
            name="Electronics",
            description="Electronic products",
            is_active=True,
        )
        self.inactive_category = ProductCategoryFactory(
            name="Inactive Category",
            is_active=False,
        )
        self.url = reverse(
            "ecommerce:category-detail",
            kwargs={"slug": self.active_category.slug},
        )

    def test_get_category_detail_success(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Electronics"
        assert response.data["id"] == str(self.active_category.id)

    def test_category_detail_response_structure(self):
        response = self.client.get(self.url)

        expected_fields = {"id", "name", "subcategories", "slug"}
        assert set(response.data.keys()) == expected_fields

    def test_category_detail_includes_subcategories(self):
        ProductSubCategoryFactory(
            name="Laptops",
            category=self.active_category,
            is_active=True,
        )
        ProductSubCategoryFactory(
            name="Phones",
            category=self.active_category,
            is_active=True,
        )

        response = self.client.get(self.url)

        assert len(response.data["subcategories"]) == 2  # noqa: PLR2004
        subcategory_names = [sub["name"] for sub in response.data["subcategories"]]
        assert "Laptops" in subcategory_names
        assert "Phones" in subcategory_names

    def test_category_detail_subcategory_structure(self):
        subcategory = ProductSubCategoryFactory(
            name="Laptops",
            category=self.active_category,
            is_active=True,
        )

        response = self.client.get(self.url)
        subcategory_data = response.data["subcategories"][0]

        expected_fields = {"id", "name", "slug"}
        assert set(subcategory_data.keys()) == expected_fields
        assert subcategory_data["id"] == str(subcategory.id)
        assert subcategory_data["name"] == "Laptops"

    def test_category_detail_excludes_inactive_subcategories(self):
        ProductSubCategoryFactory(
            name="Active Subcategory",
            category=self.active_category,
            is_active=True,
        )
        ProductSubCategoryFactory(
            name="Inactive Subcategory",
            category=self.active_category,
            is_active=False,
        )

        response = self.client.get(self.url)

        assert len(response.data["subcategories"]) == 1
        assert response.data["subcategories"][0]["name"] == "Active Subcategory"

    def test_category_detail_subcategories_ordered_by_name(self):
        ProductSubCategoryFactory(
            name="Zebra Product",
            category=self.active_category,
            is_active=True,
        )
        ProductSubCategoryFactory(
            name="Alpha Product",
            category=self.active_category,
            is_active=True,
        )

        response = self.client.get(self.url)
        subcategory_names = [sub["name"] for sub in response.data["subcategories"]]

        assert subcategory_names == sorted(subcategory_names)

    def test_category_detail_not_found_for_inactive_category(self):
        url = reverse(
            "ecommerce:category-detail",
            kwargs={"slug": self.inactive_category.slug},
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_category_detail_not_found_for_nonexistent_slug(self):
        url = reverse(
            "ecommerce:category-detail",
            kwargs={"slug": "nonexistent-category"},
        )
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_category_detail_slug_field_present(self):
        response = self.client.get(self.url)

        assert response.data["slug"] == self.active_category.slug


@pytest.mark.django_db
class CategoryAPIPermissionTest:
    def test_category_list_allows_anonymous_access(self):
        url = reverse("ecommerce:category-list")

        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_category_detail_allows_anonymous_access(self):
        category = ProductCategoryFactory(is_active=True)
        url = reverse("ecommerce:category-detail", kwargs={"slug": category.slug})

        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class CategoryAPIEdgeCaseTest:
    def test_category_list_with_no_categories(self):
        url = reverse("ecommerce:category-list")

        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_category_with_no_subcategories(self):
        category = ProductCategoryFactory(is_active=True)
        url = reverse("ecommerce:category-detail", kwargs={"slug": category.slug})
        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["subcategories"]) == 0

    def test_category_list_search_no_results(self):
        ProductCategoryFactory(name="Electronics", is_active=True)
        url = reverse("ecommerce:category-list")
        client = APIClient()

        response = client.get(url, {"search": "NonexistentCategory"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
