import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.users.tests.factories import UserFactory
from vendors.tests.factories import CompanyVendorFactory
from vendors.tests.factories import IndividualVendorFactory


@pytest.mark.django_db
class TestVendorMeAPIView:
    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.url = reverse("vendors:vendor-me")

    def test_get_vendor_me_unauthenticated(self):
        """Test that unauthenticated users cannot access vendor me endpoint."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_vendor_me_no_vendor_profile(self):
        """Test 404 response when user has no vendor profile."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "User does not have a vendor profile" in str(response.data["detail"])

    def test_get_vendor_me_individual_success(self):
        """Test successful retrieval of current user's individual vendor profile."""
        vendor = IndividualVendorFactory(user=self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == vendor.id
        assert response.data["name"] == vendor.name
        assert response.data["vendor_type"] == vendor.vendor_type
        assert response.data["full_name"] == vendor.full_name

    def test_get_vendor_me_company_success(self):
        """Test successful retrieval of current user's company vendor profile."""
        vendor = CompanyVendorFactory(user=self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == vendor.id
        assert response.data["name"] == vendor.name
        assert response.data["vendor_type"] == vendor.vendor_type
        assert response.data["business_name"] == vendor.business_name

    def test_update_vendor_me_put_unauthenticated(self):
        """Test that unauthenticated users cannot update vendor profile."""
        response = self.client.put(self.url, {})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_vendor_me_patch_unauthenticated(self):
        """Test that unauthenticated users cannot patch vendor profile."""
        response = self.client.patch(self.url, {})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_vendor_me_no_profile(self):
        """Test update when user has no vendor profile."""
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, {"name": "New Name"})

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_individual_vendor_name_patch(self):
        """Test partial update of individual vendor name."""
        vendor = IndividualVendorFactory(user=self.user, name="Old Name")

        data = {"name": "New Store Name"}

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        vendor.refresh_from_db()
        assert vendor.name == "New Store Name"

    def test_update_individual_vendor_full_name_patch(self):
        """Test partial update of individual vendor full name."""
        vendor = IndividualVendorFactory(user=self.user, full_name="Old Name")

        data = {"full_name": "John Smith"}

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        vendor.refresh_from_db()
        assert vendor.full_name == "John Smith"

    def test_update_company_vendor_business_info_patch(self):
        """Test partial update of company vendor business information."""
        vendor = CompanyVendorFactory(user=self.user)

        data = {
            "business_name": "Updated Corp",
            "business_number": "NEW123456",
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        vendor.refresh_from_db()
        assert vendor.business_name == "Updated Corp"
        assert vendor.business_number == "NEW123456"

    def test_update_vendor_location_patch(self):
        """Test partial update of vendor location."""
        from location.tests.factories import CityFactory
        from location.tests.factories import DistrictFactory
        from location.tests.factories import ProvinceFactory

        vendor = IndividualVendorFactory(user=self.user)

        new_province = ProvinceFactory()
        new_city = CityFactory(province=new_province)
        new_district = DistrictFactory(city=new_city)

        data = {
            "province": new_province.id,
            "city": new_city.id,
            "district": new_district.id,
            "address_detail": "New address detail",
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        vendor.refresh_from_db()
        assert vendor.province.id == new_province.id
        assert vendor.city.id == new_city.id
        assert vendor.district.id == new_district.id
        assert vendor.address_detail == "New address detail"

    def test_update_individual_vendor_remove_required_field(self):
        """Test validation error when removing required field from individual vendor."""
        IndividualVendorFactory(user=self.user)

        data = {"full_name": ""}  # Remove required field

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "full_name" in response.data

    def test_update_company_vendor_remove_required_field(self):
        """Test validation error when removing required field from company vendor."""
        CompanyVendorFactory(user=self.user)

        data = {"business_name": ""}  # Remove required field

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "business_name" in response.data

    def test_update_vendor_invalid_location_hierarchy(self):
        """Test validation error for invalid location hierarchy during update."""
        from location.tests.factories import CityFactory
        from location.tests.factories import ProvinceFactory

        IndividualVendorFactory(user=self.user)

        province1 = ProvinceFactory()
        province2 = ProvinceFactory()
        city_in_province2 = CityFactory(province=province2)

        data = {
            "province": province1.id,
            "city": city_in_province2.id,  # City belongs to different province
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "city" in response.data

    def test_update_vendor_me_put_success(self):
        """Test full update of vendor with PUT method."""
        from location.tests.factories import CityFactory
        from location.tests.factories import DistrictFactory
        from location.tests.factories import ProvinceFactory

        vendor = IndividualVendorFactory(user=self.user)

        province = ProvinceFactory()
        city = CityFactory(province=province)
        district = DistrictFactory(city=city)

        data = {
            "name": "Completely New Store",
            "phone_number": "082345678901",
            "address": "New Address",
            "full_name": "Jane Doe",
            "province": province.id,
            "city": city.id,
            "district": district.id,
            "latitude": "-7.250000",
            "longitude": "112.750000",
            "address_detail": "Jl. New Street No. 789",
            "postal_code": "67890",
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        vendor.refresh_from_db()
        assert vendor.name == "Completely New Store"
        assert vendor.phone_number == "082345678901"
        assert vendor.full_name == "Jane Doe"

    def test_update_vendor_readonly_fields_ignored(self):
        """Test that readonly fields are ignored during update."""
        vendor = IndividualVendorFactory(user=self.user)
        original_vendor_type = vendor.vendor_type
        original_user = vendor.user
        original_created_at = vendor.created_at

        data = {
            "name": "Updated Name",
            "vendor_type": "company",  # Should be ignored
            "user": UserFactory().id,  # Should be ignored
            "created_at": "2020-01-01T00:00:00Z",  # Should be ignored
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        vendor.refresh_from_db()
        assert vendor.name == "Updated Name"
        assert vendor.vendor_type == original_vendor_type  # Unchanged
        assert vendor.user == original_user  # Unchanged
        assert vendor.created_at == original_created_at  # Unchanged

    def test_vendor_me_response_structure(self):
        """Test the structure of vendor me response."""
        IndividualVendorFactory(user=self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

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

    def test_update_vendor_coordinates(self):
        """Test updating vendor coordinates."""
        vendor = IndividualVendorFactory(user=self.user)

        data = {
            "latitude": "-8.123456",
            "longitude": "113.654321",
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        vendor.refresh_from_db()
        assert str(vendor.latitude) == "-8.123456"
        assert str(vendor.longitude) == "113.654321"

    def test_update_vendor_postal_code(self):
        """Test updating vendor postal code."""
        vendor = IndividualVendorFactory(user=self.user)

        data = {"postal_code": "55555"}

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        vendor.refresh_from_db()
        assert vendor.postal_code == "55555"

    def test_other_user_cannot_access_vendor_me(self):
        """Test that users can only access their own vendor profile."""
        user1 = UserFactory()
        user2 = UserFactory()
        vendor1 = IndividualVendorFactory(user=user1)
        vendor2 = IndividualVendorFactory(user=user2)

        # User2 tries to access their profile - should get their own vendor
        self.client.force_authenticate(user=user2)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == vendor2.id
        assert response.data["id"] != vendor1.id

    def test_update_vendor_phone_number(self):
        """Test updating vendor phone number."""
        vendor = IndividualVendorFactory(user=self.user, phone_number="081111111111")

        data = {"phone_number": "082222222222"}

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.url, data)

        assert response.status_code == status.HTTP_200_OK
        vendor.refresh_from_db()
        assert vendor.phone_number == "082222222222"
