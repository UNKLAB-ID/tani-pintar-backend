from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from core.users.tests.factories import UserFactory
from vendors.models import Vendor
from vendors.tests.factories import CompanyVendorFactory
from vendors.tests.factories import IndividualVendorFactory
from vendors.tests.factories import VendorFactory


@pytest.mark.django_db
class TestVendorListCreateAPIView:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("vendors:vendor-list-create")
        self.user = UserFactory()

    def create_test_image(self, filename="test.jpg"):
        """Create a test image file for uploads."""
        image = Image.new("RGB", (10, 10), color="red")
        image_file = BytesIO()
        image.save(image_file, "JPEG")
        image_file.seek(0)
        return SimpleUploadedFile(
            filename,
            image_file.getvalue(),
            content_type="image/jpeg",
        )

    def test_list_vendors_unauthenticated(self):
        """Test that unauthenticated users cannot access vendor list."""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_vendors_authenticated_empty(self):
        """Test listing vendors when no vendors exist."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"] == []

    def test_list_vendors_authenticated_with_data(self):
        """Test listing vendors with data."""
        vendor1 = IndividualVendorFactory()
        vendor2 = CompanyVendorFactory()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2  # noqa: PLR2004

        # Check that both vendors are returned
        vendor_ids = [vendor["id"] for vendor in response.data["results"]]
        assert vendor1.id in vendor_ids
        assert vendor2.id in vendor_ids

    def test_list_vendors_filtering_by_vendor_type(self):
        """Test filtering vendors by vendor type."""
        individual_vendor = IndividualVendorFactory()
        company_vendor = CompanyVendorFactory()

        self.client.force_authenticate(user=self.user)

        # Filter by individual type
        response = self.client.get(self.url, {"vendor_type": "individual"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == individual_vendor.id

        # Filter by company type
        response = self.client.get(self.url, {"vendor_type": "company"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == company_vendor.id

    def test_list_vendors_filtering_by_review_status(self):
        """Test filtering vendors by review status."""
        pending_vendor = VendorFactory(review_status=Vendor.PENDING)
        approved_vendor = VendorFactory(review_status=Vendor.APPROVED)

        self.client.force_authenticate(user=self.user)

        # Filter by pending status
        response = self.client.get(self.url, {"review_status": "Pending"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == pending_vendor.id

        # Filter by approved status
        response = self.client.get(self.url, {"review_status": "Approved"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == approved_vendor.id

    def test_list_vendors_search_by_name(self):
        """Test searching vendors by name."""
        vendor1 = VendorFactory(name="Tech Store")
        VendorFactory(name="Food Market")

        self.client.force_authenticate(user=self.user)

        # Search by partial name
        response = self.client.get(self.url, {"search": "Tech"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == vendor1.id

    def test_list_vendors_search_by_business_name(self):
        """Test searching vendors by business name."""
        vendor = CompanyVendorFactory(business_name="ABC Corporation")
        VendorFactory(name="XYZ Store")

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url, {"search": "ABC"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == vendor.id

    def test_list_vendors_search_by_full_name(self):
        """Test searching vendors by full name."""
        vendor = IndividualVendorFactory(full_name="John Doe")
        VendorFactory()

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url, {"search": "John"})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == vendor.id

    def test_list_vendors_ordering_by_created_at(self):
        """Test ordering vendors by created_at."""
        vendor1 = VendorFactory()
        vendor2 = VendorFactory()

        self.client.force_authenticate(user=self.user)

        # Default ordering should be -created_at (newest first)
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert results[0]["id"] == vendor2.id  # Newer vendor first
        assert results[1]["id"] == vendor1.id

    def test_list_vendors_ordering_by_name(self):
        """Test ordering vendors by name."""
        vendor_z = VendorFactory(name="Z Store")
        vendor_a = VendorFactory(name="A Store")

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url, {"ordering": "name"})
        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert results[0]["id"] == vendor_a.id  # A comes before Z
        assert results[1]["id"] == vendor_z.id

    def test_list_vendors_response_structure(self):
        """Test the structure of vendor list response."""
        IndividualVendorFactory()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        vendor_data = response.data["results"][0]

        # Check required fields in list serializer
        expected_fields = [
            "id",
            "name",
            "vendor_type",
            "vendor_type_display",
            "review_status",
            "review_status_display",
            "province",
            "city",
            "logo",
            "created_at",
        ]
        for field in expected_fields:
            assert field in vendor_data

    def test_create_vendor_unauthenticated(self):
        """Test that unauthenticated users cannot create vendors."""
        data = {"name": "Test Store", "vendor_type": "individual"}
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_individual_vendor_success(self):
        """Test successful creation of individual vendor."""
        from location.tests.factories import CityFactory
        from location.tests.factories import DistrictFactory
        from location.tests.factories import ProvinceFactory

        province = ProvinceFactory()
        city = CityFactory(province=province)
        district = DistrictFactory(city=city)

        # Create a test image file for ID card
        id_card_image = self.create_test_image("id_card.jpg")

        data = {
            "name": "My Store",
            "vendor_type": "individual",
            "phone_number": "081234567890",
            "address": "Test Address",
            "full_name": "John Doe",
            "id_card_photo": id_card_image,
            "province": province.id,
            "city": city.id,
            "district": district.id,
            "latitude": "-6.200000",
            "longitude": "106.816666",
            "address_detail": "Jl. Test No. 123",
            "postal_code": "12345",
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Vendor.objects.filter(user=self.user).exists()

        vendor = Vendor.objects.get(user=self.user)
        assert vendor.name == "My Store"
        assert vendor.vendor_type == "individual"
        assert vendor.full_name == "John Doe"

    def test_create_company_vendor_success(self):
        """Test successful creation of company vendor."""
        from location.tests.factories import CityFactory
        from location.tests.factories import DistrictFactory
        from location.tests.factories import ProvinceFactory

        province = ProvinceFactory()
        city = CityFactory(province=province)
        district = DistrictFactory(city=city)

        # Create a test image file for business NIB
        business_nib_image = self.create_test_image("business_nib.jpg")

        data = {
            "name": "My Company Store",
            "vendor_type": "company",
            "phone_number": "081234567890",
            "address": "Company Address",
            "business_name": "ABC Corp",
            "business_number": "123456789",
            "business_nib": business_nib_image,
            "npwp": "987654321",
            "province": province.id,
            "city": city.id,
            "district": district.id,
            "latitude": "-6.200000",
            "longitude": "106.816666",
            "address_detail": "Jl. Company No. 456",
            "postal_code": "54321",
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Vendor.objects.filter(user=self.user).exists()

        vendor = Vendor.objects.get(user=self.user)
        assert vendor.name == "My Company Store"
        assert vendor.vendor_type == "company"
        assert vendor.business_name == "ABC Corp"

    def test_create_individual_vendor_missing_full_name(self):
        """Test validation error when individual vendor missing full name."""
        from location.tests.factories import CityFactory
        from location.tests.factories import DistrictFactory
        from location.tests.factories import ProvinceFactory

        province = ProvinceFactory()
        city = CityFactory(province=province)
        district = DistrictFactory(city=city)

        data = {
            "name": "My Store",
            "vendor_type": "individual",
            "phone_number": "081234567890",
            "address": "Test Address",
            "province": province.id,
            "city": city.id,
            "district": district.id,
            "latitude": "-6.200000",
            "longitude": "106.816666",
            "address_detail": "Jl. Test No. 123",
            "postal_code": "12345",
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "full_name" in response.data

    def test_create_company_vendor_missing_business_fields(self):
        """Test validation error when company vendor missing business fields."""
        from location.tests.factories import CityFactory
        from location.tests.factories import DistrictFactory
        from location.tests.factories import ProvinceFactory

        province = ProvinceFactory()
        city = CityFactory(province=province)
        district = DistrictFactory(city=city)

        data = {
            "name": "My Company",
            "vendor_type": "company",
            "phone_number": "081234567890",
            "address": "Company Address",
            "province": province.id,
            "city": city.id,
            "district": district.id,
            "latitude": "-6.200000",
            "longitude": "106.816666",
            "address_detail": "Jl. Company No. 456",
            "postal_code": "54321",
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        # Should get validation errors for missing required company fields
        # Serializer validates one field at a time, so we expect at least one error
        expected_fields = ["business_name", "business_number", "business_nib", "npwp"]
        has_any_expected_field = any(
            field in response.data for field in expected_fields
        )
        assert (
            has_any_expected_field
        ), f"Expected one of {expected_fields} in {response.data}"

    def test_create_vendor_location_hierarchy_validation_error(self):
        """Test validation error for invalid location hierarchy."""
        from location.tests.factories import CityFactory
        from location.tests.factories import DistrictFactory
        from location.tests.factories import ProvinceFactory

        province1 = ProvinceFactory()
        province2 = ProvinceFactory()
        city_in_province2 = CityFactory(province=province2)
        district_in_city = DistrictFactory(city=city_in_province2)

        id_card_image = self.create_test_image("id_card.jpg")

        data = {
            "name": "My Store",
            "vendor_type": "individual",
            "phone_number": "081234567890",
            "address": "Test Address",
            "full_name": "John Doe",
            "id_card_photo": id_card_image,
            "province": province1.id,
            "city": city_in_province2.id,  # City belongs to different province
            "district": district_in_city.id,
            "latitude": "-6.200000",
            "longitude": "106.816666",
            "address_detail": "Jl. Test No. 123",
            "postal_code": "12345",
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "city" in response.data

    def test_create_vendor_duplicate_user(self):
        """Test that user cannot create multiple vendor profiles."""
        # Create first vendor
        VendorFactory(user=self.user)

        data = {
            "name": "Second Store",
            "vendor_type": "individual",
            "phone_number": "081234567890",
            "address": "Test Address",
            "full_name": "John Doe",
        }

        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "User already has a vendor profile" in str(response.data["detail"])

    def test_list_vendors_pagination(self):
        """Test vendor list pagination."""
        # Create multiple vendors
        for _ in range(5):
            VendorFactory()

        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "next" in response.data
        assert "previous" in response.data
        assert "results" in response.data

    def test_list_vendors_filtering_by_location(self):
        """Test filtering vendors by province and city."""
        from location.tests.factories import CityFactory
        from location.tests.factories import ProvinceFactory

        province1 = ProvinceFactory()
        province2 = ProvinceFactory()
        city1 = CityFactory(province=province1)
        city2 = CityFactory(province=province2)

        vendor1 = VendorFactory(province=province1, city=city1)
        vendor2 = VendorFactory(province=province2, city=city2)

        self.client.force_authenticate(user=self.user)

        # Filter by province
        response = self.client.get(self.url, {"province": province1.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == vendor1.id

        # Filter by city
        response = self.client.get(self.url, {"city": city2.id})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == vendor2.id
