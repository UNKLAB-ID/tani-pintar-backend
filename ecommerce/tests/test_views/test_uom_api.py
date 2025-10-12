import uuid

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from ecommerce.tests.factories import UnitOfMeasureFactory


class UnitOfMeasureListAPITest(APITestCase):
    def setUp(self):
        self.url = reverse("ecommerce:uom-list")
        self.uom_kg = UnitOfMeasureFactory(name="kilogram")
        self.uom_liter = UnitOfMeasureFactory(name="liter")
        self.uom_piece = UnitOfMeasureFactory(name="piece")

    def test_get_uom_list_success(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3  # noqa: PLR2004

    def test_uom_list_response_structure(self):
        response = self.client.get(self.url)

        assert isinstance(response.data, list)
        assert len(response.data) >= 0

    def test_uom_list_item_structure(self):
        response = self.client.get(self.url)
        uom = response.data[0]

        expected_fields = {"id", "name"}
        assert set(uom.keys()) == expected_fields

    def test_uom_list_ordered_by_name(self):
        response = self.client.get(self.url)

        uom_names = [uom["name"] for uom in response.data]
        assert uom_names == sorted(uom_names)
        # Should be: kilogram, liter, piece (alphabetically)
        assert uom_names == ["kilogram", "liter", "piece"]

    def test_uom_list_returns_all_uoms(self):
        response = self.client.get(self.url)

        uom_names = [uom["name"] for uom in response.data]
        assert "kilogram" in uom_names
        assert "liter" in uom_names
        assert "piece" in uom_names

    def test_uom_list_response_contains_valid_uuids(self):
        response = self.client.get(self.url)

        for uom in response.data:
            # Verify that id is a valid UUID string
            assert isinstance(uom["id"], str)
            uuid.UUID(uom["id"])  # Should not raise ValueError


class UnitOfMeasureDetailAPITest(APITestCase):
    def setUp(self):
        self.uom = UnitOfMeasureFactory(
            name="kilogram",
            description="Unit of mass",
        )
        self.url = reverse("ecommerce:uom-detail", kwargs={"pk": self.uom.id})

    def test_get_uom_detail_success(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "kilogram"
        assert response.data["id"] == str(self.uom.id)

    def test_uom_detail_response_structure(self):
        response = self.client.get(self.url)

        expected_fields = {"id", "name"}
        assert set(response.data.keys()) == expected_fields

    def test_uom_detail_with_valid_uuid(self):
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        # Verify the UUID is properly formatted
        assert uuid.UUID(response.data["id"]) == self.uom.id

    def test_uom_detail_not_found_for_nonexistent_uuid(self):
        nonexistent_uuid = uuid.uuid4()
        url = reverse("ecommerce:uom-detail", kwargs={"pk": nonexistent_uuid})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_uom_detail_id_field_is_uuid_string(self):
        response = self.client.get(self.url)

        assert isinstance(response.data["id"], str)
        assert response.data["id"] == str(self.uom.id)

    def test_uom_detail_name_field_present(self):
        response = self.client.get(self.url)

        assert "name" in response.data
        assert response.data["name"] == self.uom.name


@pytest.mark.django_db
class UnitOfMeasureAPIPermissionTest:
    def test_uom_list_allows_anonymous_access(self):
        url = reverse("ecommerce:uom-list")
        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_uom_detail_allows_anonymous_access(self):
        uom = UnitOfMeasureFactory(name="kilogram")
        url = reverse("ecommerce:uom-detail", kwargs={"pk": uom.id})
        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class UnitOfMeasureAPIEdgeCaseTest:
    def test_uom_list_with_no_uoms(self):
        url = reverse("ecommerce:uom-list")
        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_uom_list_with_many_uoms(self):
        # Create multiple UOMs
        for i in range(10):
            UnitOfMeasureFactory(name=f"unit_{i}")

        url = reverse("ecommerce:uom-list")
        client = APIClient()

        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 10  # noqa: PLR2004

    def test_uom_list_ordering_with_multiple_uoms(self):
        # Create UOMs in non-alphabetical order
        UnitOfMeasureFactory(name="zebra-unit")
        UnitOfMeasureFactory(name="alpha-unit")
        UnitOfMeasureFactory(name="beta-unit")

        url = reverse("ecommerce:uom-list")
        client = APIClient()

        response = client.get(url)
        uom_names = [uom["name"] for uom in response.data]

        # Should be ordered alphabetically
        assert uom_names == ["alpha-unit", "beta-unit", "zebra-unit"]

    def test_uom_detail_returns_only_specified_fields(self):
        uom = UnitOfMeasureFactory(
            name="kilogram",
            description="This description should not be in detail response",
        )
        url = reverse("ecommerce:uom-detail", kwargs={"pk": uom.id})
        client = APIClient()

        response = client.get(url)

        # Only id and name should be returned, not description
        assert set(response.data.keys()) == {"id", "name"}
        assert "description" not in response.data
        assert "created_at" not in response.data
        assert "updated_at" not in response.data
