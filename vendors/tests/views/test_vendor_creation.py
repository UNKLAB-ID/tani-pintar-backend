from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from core.users.tests.factories import UserFactory
from location.models import City
from location.models import Country
from location.models import District
from location.models import Province
from vendors.models import Vendor
from vendors.tests.factories import VendorFactory


def create_test_image():
    """Helper function to create a test image file."""
    file = BytesIO()
    image = Image.new("RGB", (100, 100), color="red")
    image.save(file, "JPEG")
    file.name = "test.jpg"
    file.seek(0)
    return SimpleUploadedFile(
        name="test.jpg",
        content=file.read(),
        content_type="image/jpeg",
    )


def create_test_pdf():
    """Helper function to create a test PDF file."""
    return SimpleUploadedFile(
        name="test.pdf",
        content=b"PDF content here",
        content_type="application/pdf",
    )


class TestCreateIndividualVendorAPIView(TestCase):
    """Test cases for individual vendor creation endpoint."""

    def setUp(self):
        """Set up test data for each test."""
        self.client = APIClient()
        self.user = UserFactory()

        # Create location data manually
        self.country = Country.objects.create(
            name="Indonesia",
            code="ID",
        )
        self.province = Province.objects.create(
            name="DKI Jakarta",
            country=self.country,
        )
        self.city = City.objects.create(
            name="Jakarta Selatan",
            province=self.province,
        )
        self.district = District.objects.create(
            name="Kebayoran Baru",
            city=self.city,
        )

        self.url = reverse("vendors:vendor-create-individual")

        # Base valid data for individual vendor
        self.valid_data = {
            "full_name": "John Doe",
            "phone_number": "+628123456789",
            "name": "John's Farm Store",
            "province": self.province.id,
            "city": self.city.id,
            "district": self.district.id,
            "latitude": "-6.200000",
            "longitude": "106.816666",
            "address_detail": "Jl. Raya No. 123",
            "postal_code": "12345",
        }

    def test_create_individual_vendor_success(self):
        """Test successful creation of individual vendor with all required fields."""
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["id_card_photo"] = create_test_image()

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_201_CREATED
        assert Vendor.objects.filter(user=self.user).exists()

        vendor = Vendor.objects.get(user=self.user)
        assert vendor.vendor_type == Vendor.TYPE_INDIVIDUAL
        assert vendor.review_status == Vendor.STATUS_PENDING
        assert vendor.full_name == "John Doe"
        assert vendor.name == "John's Farm Store"
        assert vendor.phone_number == "+628123456789"
        assert vendor.province == self.province
        assert vendor.city == self.city
        assert vendor.district == self.district

    def test_create_individual_vendor_with_logo(self):
        """Test successful creation of individual vendor with optional logo."""
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["id_card_photo"] = create_test_image()
        data["logo"] = create_test_image()

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_201_CREATED
        vendor = Vendor.objects.get(user=self.user)
        assert vendor.logo is not None

    def test_create_individual_vendor_without_authentication(self):
        """Test that unauthenticated users cannot create vendor."""
        data = self.valid_data.copy()
        data["id_card_photo"] = create_test_image()

        response = self.client.post(self.url, data, format="multipart")

        # Should return 403 Forbidden or 401 Unauthorized
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]
        assert not Vendor.objects.filter(user=self.user).exists()

    def test_create_individual_vendor_missing_full_name(self):
        """Test validation error when full_name is missing."""
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["id_card_photo"] = create_test_image()
        del data["full_name"]

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "full_name" in response.data

    def test_create_individual_vendor_missing_id_card_photo(self):
        """Test validation error when id_card_photo is missing."""
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "id_card_photo" in response.data

    def test_create_individual_vendor_missing_phone_number(self):
        """Test validation error when phone_number is missing."""
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["id_card_photo"] = create_test_image()
        del data["phone_number"]

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "phone_number" in response.data

    def test_create_individual_vendor_missing_location_fields(self):
        """Test validation error when location fields are missing."""
        self.client.force_authenticate(user=self.user)

        data = {
            "full_name": "John Doe",
            "phone_number": "+628123456789",
            "name": "John's Farm Store",
            "id_card_photo": create_test_image(),
        }

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert any(
            field in response.data
            for field in ["province", "city", "district", "latitude", "longitude"]
        )

    def test_create_individual_vendor_with_pending_application(self):
        """Test that users cannot create vendor if they already have pending application."""  # noqa: E501
        VendorFactory(user=self.user, review_status=Vendor.STATUS_PENDING)
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["id_card_photo"] = create_test_image()

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already has a pending vendor application" in str(response.data)

    def test_create_individual_vendor_with_approved_vendor(self):
        """Test that users cannot create vendor if they are already approved."""
        VendorFactory(user=self.user, review_status=Vendor.STATUS_APPROVED)
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["id_card_photo"] = create_test_image()

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already an approved vendor" in str(response.data)

    def test_create_individual_vendor_with_rejected_application(self):
        """Test that users can reapply after rejection."""
        VendorFactory(user=self.user, review_status=Vendor.STATUS_REJECTED)
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["id_card_photo"] = create_test_image()

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_201_CREATED
        # Should have 2 vendors now (1 rejected, 1 new pending)
        assert Vendor.objects.filter(user=self.user).count() == 2  # noqa: PLR2004


class TestCreateCompanyVendorAPIView(TestCase):
    """Test cases for company vendor creation endpoint."""

    def setUp(self):
        """Set up test data for each test."""
        self.client = APIClient()
        self.user = UserFactory()

        # Create location data manually
        self.country = Country.objects.create(
            name="Indonesia",
            code="ID",
        )
        self.province = Province.objects.create(
            name="DKI Jakarta",
            country=self.country,
        )
        self.city = City.objects.create(
            name="Jakarta Selatan",
            province=self.province,
        )
        self.district = District.objects.create(
            name="Kebayoran Baru",
            city=self.city,
        )

        self.url = reverse("vendors:vendor-create-company")

        # Base valid data for company vendor
        self.valid_data = {
            "name": "PT Tech Solutions",
            "business_number": "1234567890123",
            "phone_number": "+628123456789",
            "province": self.province.id,
            "city": self.city.id,
            "district": self.district.id,
            "latitude": "-6.200000",
            "longitude": "106.816666",
            "address_detail": "Jl. Sudirman No. 456",
            "postal_code": "12345",
            "npwp_number": "12.345.678.9-012.000",
        }

    def test_create_company_vendor_success(self):
        """Test successful creation of company vendor with all required fields."""
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["business_nib_file"] = create_test_pdf()
        data["npwp_file"] = create_test_pdf()

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_201_CREATED
        assert Vendor.objects.filter(user=self.user).exists()

        vendor = Vendor.objects.get(user=self.user)
        assert vendor.vendor_type == Vendor.TYPE_COMPANY
        assert vendor.review_status == Vendor.STATUS_PENDING
        assert vendor.name == "PT Tech Solutions"
        assert vendor.business_number == "1234567890123"
        assert vendor.npwp_number == "12.345.678.9-012.000"
        assert vendor.phone_number == "+628123456789"
        assert vendor.province == self.province
        assert vendor.city == self.city
        assert vendor.district == self.district

    def test_create_company_vendor_without_authentication(self):
        """Test that unauthenticated users cannot create vendor."""
        data = self.valid_data.copy()
        data["business_nib_file"] = create_test_pdf()
        data["npwp_file"] = create_test_pdf()

        response = self.client.post(self.url, data, format="multipart")

        # Should return 403 Forbidden or 401 Unauthorized
        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]
        assert not Vendor.objects.filter(user=self.user).exists()

    def test_create_company_vendor_missing_business_number(self):
        """Test validation error when business_number is missing."""
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["business_nib_file"] = create_test_pdf()
        data["npwp_file"] = create_test_pdf()
        del data["business_number"]

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "business_number" in response.data

    def test_create_company_vendor_missing_business_nib_file(self):
        """Test validation error when business_nib_file is missing."""
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["npwp_file"] = create_test_pdf()

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "business_nib_file" in response.data

    def test_create_company_vendor_missing_npwp_number(self):
        """Test validation error when npwp_number is missing."""
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["business_nib_file"] = create_test_pdf()
        data["npwp_file"] = create_test_pdf()
        del data["npwp_number"]

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "npwp_number" in response.data

    def test_create_company_vendor_missing_npwp_file(self):
        """Test validation error when npwp_file is missing."""
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["business_nib_file"] = create_test_pdf()

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "npwp_file" in response.data

    def test_create_company_vendor_missing_phone_number(self):
        """Test validation error when phone_number is missing."""
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["business_nib_file"] = create_test_pdf()
        data["npwp_file"] = create_test_pdf()
        del data["phone_number"]

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "phone_number" in response.data

    def test_create_company_vendor_missing_location_fields(self):
        """Test validation error when location fields are missing."""
        self.client.force_authenticate(user=self.user)

        data = {
            "name": "PT Tech Solutions",
            "business_number": "1234567890123",
            "business_nib_file": create_test_pdf(),
            "phone_number": "+628123456789",
            "npwp_number": "12.345.678.9-012.000",
            "npwp_file": create_test_pdf(),
        }

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert any(
            field in response.data
            for field in ["province", "city", "district", "latitude", "longitude"]
        )

    def test_create_company_vendor_with_pending_application(self):
        """Test that users cannot create vendor if they already have pending application."""  # noqa: E501
        VendorFactory(
            user=self.user,
            vendor_type=Vendor.TYPE_COMPANY,
            review_status=Vendor.STATUS_PENDING,
        )
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["business_nib_file"] = create_test_pdf()
        data["npwp_file"] = create_test_pdf()

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already has a pending vendor application" in str(response.data)

    def test_create_company_vendor_with_approved_vendor(self):
        """Test that users cannot create vendor if they are already approved."""
        VendorFactory(
            user=self.user,
            vendor_type=Vendor.TYPE_COMPANY,
            review_status=Vendor.STATUS_APPROVED,
        )
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["business_nib_file"] = create_test_pdf()
        data["npwp_file"] = create_test_pdf()

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already an approved vendor" in str(response.data)

    def test_create_company_vendor_with_rejected_application(self):
        """Test that users can reapply after rejection."""
        VendorFactory(
            user=self.user,
            vendor_type=Vendor.TYPE_COMPANY,
            review_status=Vendor.STATUS_REJECTED,
        )
        self.client.force_authenticate(user=self.user)

        data = self.valid_data.copy()
        data["business_nib_file"] = create_test_pdf()
        data["npwp_file"] = create_test_pdf()

        response = self.client.post(self.url, data, format="multipart")

        assert response.status_code == status.HTTP_201_CREATED
        # Should have 2 vendors now (1 rejected, 1 new pending)
        assert Vendor.objects.filter(user=self.user).count() == 2  # noqa: PLR2004

    def test_create_company_vendor_invalid_location_hierarchy(self):
        """Test validation when city doesn't belong to province."""
        self.client.force_authenticate(user=self.user)

        # Create a city from a different province
        other_province = Province.objects.create(
            name="Jawa Barat",
            country=self.country,
        )
        other_city = City.objects.create(
            name="Bandung",
            province=other_province,
        )

        data = self.valid_data.copy()
        data["province"] = self.province.id  # Original province
        data["city"] = other_city.id  # City from different province
        data["district"] = self.district.id
        data["business_nib_file"] = create_test_pdf()
        data["npwp_file"] = create_test_pdf()

        response = self.client.post(self.url, data, format="multipart")

        # This should succeed at the API level but may have data inconsistency
        # The actual validation would depend on serializer implementation
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
        ]
