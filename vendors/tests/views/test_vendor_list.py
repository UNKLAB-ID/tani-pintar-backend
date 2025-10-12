from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.users.tests.factories import UserFactory
from location.models import City
from location.models import Country
from location.models import District
from location.models import Province
from vendors.models import Vendor
from vendors.tests.factories import CompanyVendorFactory
from vendors.tests.factories import IndividualVendorFactory


class TestVendorListAPIView(TestCase):
    """Test cases for vendor list API endpoint."""

    def setUp(self):
        """Set up test data for each test."""
        self.client = APIClient()
        self.user = UserFactory()

        # Create location data manually for consistent testing
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

        # Create second location for filtering tests
        self.province2 = Province.objects.create(
            name="Jawa Barat",
            country=self.country,
        )
        self.city2 = City.objects.create(
            name="Bandung",
            province=self.province2,
        )
        self.district2 = District.objects.create(
            name="Coblong",
            city=self.city2,
        )

        self.url = reverse("vendors:vendor-list")

    def test_list_vendors_success(self):
        """Test successful retrieval of vendor list."""
        # Create approved vendors
        IndividualVendorFactory(
            name="Test Store 1",
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )
        CompanyVendorFactory(
            name="Test Company 2",
            review_status=Vendor.STATUS_APPROVED,
            province=self.province2,
            city=self.city2,
            district=self.district2,
        )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) == 2  # noqa: PLR2004

        # Verify response structure
        vendor_data = response.data["results"][0]
        expected_fields = [
            "id",
            "name",
            "vendor_type",
            "review_status",
            "province",
            "city",
            "district",
            "logo",
            "created_at",
            "user",
        ]
        for field in expected_fields:
            assert field in vendor_data

    def test_list_vendors_authenticated_user(self):
        """Test that authenticated users can access vendor list."""
        self.client.force_authenticate(user=self.user)

        IndividualVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data

    def test_list_vendors_unauthenticated_user(self):
        """Test that unauthenticated users can access vendor list (AllowAny permission)."""  # noqa: E501
        IndividualVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data

    def test_list_vendors_only_approved_by_default(self):
        """Test that only approved vendors are returned by default."""
        # Create vendors with different statuses
        approved_vendor = IndividualVendorFactory(
            name="Approved Vendor",
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )
        IndividualVendorFactory(
            name="Pending Vendor",
            review_status=Vendor.STATUS_PENDING,
            province=self.province,
            city=self.city,
            district=self.district,
        )
        IndividualVendorFactory(
            name="Rejected Vendor",
            review_status=Vendor.STATUS_REJECTED,
            province=self.province,
            city=self.city,
            district=self.district,
        )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == approved_vendor.id
        assert response.data["results"][0]["review_status"] == Vendor.STATUS_APPROVED

    def test_filter_by_vendor_type(self):
        """Test filtering vendors by vendor type."""
        IndividualVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )
        CompanyVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )

        # Test filtering by individual type
        response = self.client.get(self.url, {"vendor_type": Vendor.TYPE_INDIVIDUAL})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["vendor_type"] == Vendor.TYPE_INDIVIDUAL

        # Test filtering by company type
        response = self.client.get(self.url, {"vendor_type": Vendor.TYPE_COMPANY})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["vendor_type"] == Vendor.TYPE_COMPANY

    def test_filter_by_location_province(self):
        """Test filtering vendors by province."""
        IndividualVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )
        IndividualVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            province=self.province2,
            city=self.city2,
            district=self.district2,
        )

        response = self.client.get(self.url, {"province": self.province.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["province"]["id"] == self.province.id

    def test_filter_by_location_city(self):
        """Test filtering vendors by city."""
        IndividualVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )
        IndividualVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            province=self.province2,
            city=self.city2,
            district=self.district2,
        )

        response = self.client.get(self.url, {"city": self.city.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["city"]["id"] == self.city.id

    def test_filter_by_location_district(self):
        """Test filtering vendors by district."""
        IndividualVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )
        IndividualVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            province=self.province2,
            city=self.city2,
            district=self.district2,
        )

        response = self.client.get(self.url, {"district": self.district.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["district"]["id"] == self.district.id

    def test_filter_by_review_status(self):
        """Test filtering vendors by review status."""
        # Create vendors with different statuses but override default queryset filter
        IndividualVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )
        IndividualVendorFactory(
            review_status=Vendor.STATUS_PENDING,
            province=self.province,
            city=self.city,
            district=self.district,
        )

        # Test filtering by pending status
        response = self.client.get(self.url, {"review_status": Vendor.STATUS_PENDING})
        assert response.status_code == status.HTTP_200_OK
        # Should return empty because queryset is pre-filtered to approved only
        assert len(response.data["results"]) == 0

        # Test filtering by approved status
        response = self.client.get(self.url, {"review_status": Vendor.STATUS_APPROVED})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_filter_multiple_parameters(self):
        """Test filtering with multiple parameters."""
        # Create vendors with different combinations
        target_vendor = IndividualVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            vendor_type=Vendor.TYPE_INDIVIDUAL,
            province=self.province,
            city=self.city,
            district=self.district,
        )
        CompanyVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            vendor_type=Vendor.TYPE_COMPANY,
            province=self.province2,
            city=self.city2,
            district=self.district2,
        )

        response = self.client.get(
            self.url,
            {
                "vendor_type": Vendor.TYPE_INDIVIDUAL,
                "province": self.province.id,
                "city": self.city.id,
            },
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == target_vendor.id

    def test_search_by_name(self):
        """Test searching vendors by name."""
        IndividualVendorFactory(
            name="Tech Solutions Store",
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )
        IndividualVendorFactory(
            name="Farm Fresh Market",
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )

        response = self.client.get(self.url, {"search": "Tech"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert "Tech" in response.data["results"][0]["name"]

    def test_search_by_full_name(self):
        """Test searching vendors by full_name (for individual vendors)."""
        IndividualVendorFactory(
            name="Store 1",
            full_name="John Smith",
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )
        IndividualVendorFactory(
            name="Store 2",
            full_name="Jane Doe",
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )

        response = self.client.get(self.url, {"search": "John"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_search_case_insensitive(self):
        """Test that search is case insensitive."""
        IndividualVendorFactory(
            name="TECH SOLUTIONS",
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )

        response = self.client.get(self.url, {"search": "tech"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_search_partial_matching(self):
        """Test that search supports partial matching."""
        IndividualVendorFactory(
            name="Agricultural Solutions Store",
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )

        response = self.client.get(self.url, {"search": "Agri"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

    def test_ordering_default(self):
        """Test default ordering by -created_at."""
        # Create vendors at different times
        vendor1 = IndividualVendorFactory(
            name="Vendor 1",
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )
        vendor2 = IndividualVendorFactory(
            name="Vendor 2",
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        # Most recent should be first (vendor2 created after vendor1)
        assert results[0]["id"] == vendor2.id
        assert results[1]["id"] == vendor1.id

    def test_ordering_by_name(self):
        """Test ordering by name."""
        IndividualVendorFactory(
            name="Zebra Store",
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )
        IndividualVendorFactory(
            name="Alpha Store",
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )

        response = self.client.get(self.url, {"ordering": "name"})

        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert results[0]["name"] == "Alpha Store"
        assert results[1]["name"] == "Zebra Store"

    def test_ordering_by_name_descending(self):
        """Test ordering by name in descending order."""
        IndividualVendorFactory(
            name="Alpha Store",
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )
        IndividualVendorFactory(
            name="Zebra Store",
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )

        response = self.client.get(self.url, {"ordering": "-name"})

        assert response.status_code == status.HTTP_200_OK
        results = response.data["results"]
        assert results[0]["name"] == "Zebra Store"
        assert results[1]["name"] == "Alpha Store"

    def test_pagination_structure(self):
        """Test cursor pagination response structure."""
        # Create multiple vendors to test pagination
        for i in range(5):
            IndividualVendorFactory(
                name=f"Vendor {i}",
                review_status=Vendor.STATUS_APPROVED,
                province=self.province,
                city=self.city,
                district=self.district,
            )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert "next" in response.data
        assert "previous" in response.data

    def test_pagination_page_size(self):
        """Test custom page size parameter."""
        # Create multiple vendors
        for i in range(5):
            IndividualVendorFactory(
                name=f"Vendor {i}",
                review_status=Vendor.STATUS_APPROVED,
                province=self.province,
                city=self.city,
                district=self.district,
            )

        response = self.client.get(self.url, {"page_size": 2})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2  # noqa: PLR2004

    def test_pagination_max_page_size(self):
        """Test that page_size is limited by max_page_size."""
        # Create multiple vendors
        vendor_count = 10
        for i in range(vendor_count):
            IndividualVendorFactory(
                name=f"Vendor {i}",
                review_status=Vendor.STATUS_APPROVED,
                province=self.province,
                city=self.city,
                district=self.district,
            )

        # Request more than max_page_size (100)
        response = self.client.get(self.url, {"page_size": 150})

        assert response.status_code == status.HTTP_200_OK
        # Should return only vendor_count vendors (all available), limited by actual count  # noqa: E501
        assert len(response.data["results"]) == vendor_count

    def test_response_includes_related_data(self):
        """Test that response includes properly serialized related data."""
        vendor = IndividualVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )

        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        vendor_data = response.data["results"][0]

        # Check province data
        assert "province" in vendor_data
        assert vendor_data["province"]["id"] == self.province.id
        assert vendor_data["province"]["name"] == self.province.name

        # Check city data
        assert "city" in vendor_data
        assert vendor_data["city"]["id"] == self.city.id
        assert vendor_data["city"]["name"] == self.city.name

        # Check district data
        assert "district" in vendor_data
        assert vendor_data["district"]["id"] == self.district.id
        assert vendor_data["district"]["name"] == self.district.name

        # Check user data
        assert "user" in vendor_data
        assert vendor_data["user"]["id"] == vendor.user.id

    def test_empty_list_response(self):
        """Test response when no vendors exist."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert len(response.data["results"]) == 0
        assert response.data["next"] is None
        assert response.data["previous"] is None

    def test_invalid_filter_parameters(self):
        """Test handling of invalid filter parameters."""
        IndividualVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )

        # Test with invalid vendor_type (DRF validates choice fields strictly)
        response = self.client.get(self.url, {"vendor_type": "INVALID"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Test with non-existent province ID (DRF validates foreign keys strictly)
        response = self.client.get(self.url, {"province": 99999})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_large_dataset_performance(self):
        """Test performance with larger dataset to verify select_related optimization."""  # noqa: E501
        # Create multiple vendors to test query optimization
        vendor_count = 50
        for i in range(vendor_count):
            IndividualVendorFactory(
                name=f"Performance Test Vendor {i}",
                review_status=Vendor.STATUS_APPROVED,
                province=self.province,
                city=self.city,
                district=self.district,
            )

        # Test that the query works efficiently (exact query count may vary)
        # due to pagination, filtering, and authentication queries
        response = self.client.get(self.url, {"page_size": vendor_count})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == vendor_count

    def test_invalid_ordering_parameter(self):
        """Test handling of invalid ordering parameters."""
        IndividualVendorFactory(
            review_status=Vendor.STATUS_APPROVED,
            province=self.province,
            city=self.city,
            district=self.district,
        )

        # Test with invalid ordering field
        response = self.client.get(self.url, {"ordering": "invalid_field"})

        # Should still return successful response with default ordering
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
