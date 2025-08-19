import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.users.tests.factories import UserFactory
from vendors.tests.factories import CompanyVendorFactory
from vendors.tests.factories import IndividualVendorFactory


@pytest.mark.django_db
class TestVendorDetailAPIView:
    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()

    def test_get_vendor_detail_unauthenticated(self):
        """Test that unauthenticated users cannot access vendor detail."""
        vendor = IndividualVendorFactory()
        url = reverse("vendors:vendor-detail", kwargs={"pk": vendor.pk})

        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_individual_vendor_detail_success(self):
        """Test successful retrieval of individual vendor details."""
        vendor = IndividualVendorFactory()
        url = reverse("vendors:vendor-detail", kwargs={"pk": vendor.pk})

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == vendor.id
        assert response.data["name"] == vendor.name
        assert response.data["vendor_type"] == vendor.vendor_type
        assert response.data["full_name"] == vendor.full_name
        assert response.data["business_name"] == vendor.business_name

    def test_get_company_vendor_detail_success(self):
        """Test successful retrieval of company vendor details."""
        vendor = CompanyVendorFactory()
        url = reverse("vendors:vendor-detail", kwargs={"pk": vendor.pk})

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == vendor.id
        assert response.data["name"] == vendor.name
        assert response.data["vendor_type"] == vendor.vendor_type
        assert response.data["business_name"] == vendor.business_name
        assert response.data["business_number"] == vendor.business_number
        assert response.data["npwp"] == vendor.npwp

    def test_get_vendor_detail_not_found(self):
        """Test 404 response for non-existent vendor."""
        url = reverse("vendors:vendor-detail", kwargs={"pk": 99999})

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_vendor_detail_response_structure(self):
        """Test the structure of vendor detail response."""
        vendor = IndividualVendorFactory()
        url = reverse("vendors:vendor-detail", kwargs={"pk": vendor.pk})

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Check all expected fields are present
        expected_fields = [
            "id",
            "user",
            "name",
            "vendor_type",
            "vendor_type_display",
            "phone_number",
            "address",
            "logo",
            "full_name",
            "id_card_photo",
            "business_name",
            "business_number",
            "business_nib",
            "npwp",
            "province",
            "city",
            "district",
            "latitude",
            "longitude",
            "address_detail",
            "postal_code",
            "review_status",
            "review_status_display",
            "review_notes",
            "created_at",
            "updated_at",
        ]

        for field in expected_fields:
            assert field in response.data, f"Field '{field}' missing from response"

    def test_vendor_detail_location_serialization(self):
        """Test that location fields are properly serialized."""
        vendor = IndividualVendorFactory()
        url = reverse("vendors:vendor-detail", kwargs={"pk": vendor.pk})

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK

        # Check location serialization
        assert response.data["province"]["id"] == vendor.province.id
        assert response.data["province"]["name"] == vendor.province.name
        assert response.data["city"]["id"] == vendor.city.id
        assert response.data["city"]["name"] == vendor.city.name
        assert response.data["district"]["id"] == vendor.district.id
        assert response.data["district"]["name"] == vendor.district.name

    def test_vendor_detail_user_serialization(self):
        """Test that user field is properly serialized."""
        vendor = IndividualVendorFactory()
        url = reverse("vendors:vendor-detail", kwargs={"pk": vendor.pk})

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"] == str(vendor.user)

    def test_vendor_detail_display_fields(self):
        """Test that display fields show proper values."""
        vendor = IndividualVendorFactory(vendor_type="individual")
        url = reverse("vendors:vendor-detail", kwargs={"pk": vendor.pk})

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["vendor_type_display"] == "Individual"
        assert response.data["review_status_display"] in [
            "Pending",
            "Approved",
            "Rejected",
            "Resubmission",
        ]

    def test_vendor_detail_different_users_access(self):
        """Test that any authenticated user can view vendor details."""
        vendor = IndividualVendorFactory()
        other_user = UserFactory()
        url = reverse("vendors:vendor-detail", kwargs={"pk": vendor.pk})

        # Different user should still be able to view vendor details
        self.client.force_authenticate(user=other_user)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == vendor.id

    def test_vendor_detail_with_review_notes(self):
        """Test vendor detail with review notes."""
        review_notes = "Documents verified and approved"
        vendor = IndividualVendorFactory(
            review_status="Approved",
            review_notes=review_notes,
        )
        url = reverse("vendors:vendor-detail", kwargs={"pk": vendor.pk})

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["review_notes"] == review_notes
        assert response.data["review_status"] == "Approved"

    def test_vendor_detail_coordinates_format(self):
        """Test that coordinates are returned in proper format."""
        vendor = IndividualVendorFactory()
        url = reverse("vendors:vendor-detail", kwargs={"pk": vendor.pk})

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data["latitude"], str)
        assert isinstance(response.data["longitude"], str)

    def test_vendor_detail_timestamps(self):
        """Test that timestamps are included in response."""
        vendor = IndividualVendorFactory()
        url = reverse("vendors:vendor-detail", kwargs={"pk": vendor.pk})

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "created_at" in response.data
        assert "updated_at" in response.data
        assert response.data["created_at"] is not None
        assert response.data["updated_at"] is not None
