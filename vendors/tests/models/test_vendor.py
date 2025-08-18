import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase

from vendors.models import Vendor
from vendors.tests.factories import CompanyVendorFactory
from vendors.tests.factories import IndividualVendorFactory
from vendors.tests.factories import VendorFactory


class TestVendorModel(TestCase):
    def test_vendor_creation_with_factory(self):
        """Test that vendor can be created successfully with factory."""
        vendor = VendorFactory()
        assert vendor.id is not None
        assert vendor.name
        assert vendor.user
        assert vendor.review_status == Vendor.PENDING

    def test_vendor_str_representation(self):
        """Test vendor string representation."""
        vendor = VendorFactory(name="Test Store", vendor_type=Vendor.TYPE_INDIVIDUAL)
        expected = f"{vendor.name} ({vendor.get_vendor_type_display()})"
        assert str(vendor) == expected

    def test_individual_vendor_creation(self):
        """Test individual vendor creation with required fields."""
        vendor = IndividualVendorFactory()
        assert vendor.vendor_type == Vendor.TYPE_INDIVIDUAL
        assert vendor.full_name
        assert vendor.id_card_photo
        assert vendor.business_name == ""
        assert vendor.business_number == ""

    def test_company_vendor_creation(self):
        """Test company vendor creation with required fields."""
        vendor = CompanyVendorFactory()
        assert vendor.vendor_type == Vendor.TYPE_COMPANY
        assert vendor.business_name
        assert vendor.business_number
        assert vendor.business_nib
        assert vendor.npwp
        assert vendor.full_name == ""

    def test_individual_vendor_validation_success(self):
        """Test that individual vendor passes validation with required fields."""
        vendor = IndividualVendorFactory()
        vendor.clean()

    def test_company_vendor_validation_success(self):
        """Test that company vendor passes validation with required fields."""
        vendor = CompanyVendorFactory()
        vendor.clean()

    def test_individual_vendor_missing_full_name(self):
        """Test validation fails when individual vendor missing full name."""
        vendor = IndividualVendorFactory(full_name="")
        with pytest.raises(ValidationError) as context:
            vendor.clean()
        assert "full_name" in context.value.message_dict

    def test_individual_vendor_missing_id_card_photo(self):
        """Test validation fails when individual vendor missing ID card photo."""
        vendor = IndividualVendorFactory(id_card_photo=None)
        with pytest.raises(ValidationError) as context:
            vendor.clean()
        assert "id_card_photo" in context.value.message_dict

    def test_company_vendor_missing_business_name(self):
        """Test validation fails when company vendor missing business name."""
        vendor = CompanyVendorFactory(business_name="")
        with pytest.raises(ValidationError) as context:
            vendor.clean()
        assert "business_name" in context.value.message_dict

    def test_company_vendor_missing_business_number(self):
        """Test validation fails when company vendor missing business number."""
        vendor = CompanyVendorFactory(business_number="")
        with pytest.raises(ValidationError) as context:
            vendor.clean()
        assert "business_number" in context.value.message_dict

    def test_company_vendor_missing_npwp(self):
        """Test validation fails when company vendor missing NPWP."""
        vendor = CompanyVendorFactory(npwp="")
        with pytest.raises(ValidationError) as context:
            vendor.clean()
        assert "npwp" in context.value.message_dict

    def test_review_status_choices(self):
        """Test all review status choices work correctly."""
        for status, _ in Vendor.REVIEW_STATUS_CHOICES:
            vendor = VendorFactory(review_status=status)
            assert vendor.review_status == status

    def test_vendor_type_choices(self):
        """Test all vendor type choices work correctly."""
        individual_vendor = VendorFactory(vendor_type=Vendor.TYPE_INDIVIDUAL)
        company_vendor = VendorFactory(vendor_type=Vendor.TYPE_COMPANY)

        assert individual_vendor.vendor_type == Vendor.TYPE_INDIVIDUAL
        assert company_vendor.vendor_type == Vendor.TYPE_COMPANY

    def test_vendor_review_notes(self):
        """Test review notes field functionality."""
        notes = "Approved after document verification"
        vendor = VendorFactory(
            review_status=Vendor.APPROVED,
            review_notes=notes,
        )
        assert vendor.review_notes == notes

    def test_vendor_location_fields(self):
        """Test vendor location fields are properly set."""
        vendor = VendorFactory()
        assert vendor.province
        assert vendor.city
        assert vendor.district
        assert vendor.latitude
        assert vendor.longitude
        assert vendor.address
        assert vendor.address_detail
        assert vendor.postal_code

    def test_vendor_timestamps(self):
        """Test vendor has created_at and updated_at timestamps."""
        vendor = VendorFactory()
        assert vendor.created_at
        assert vendor.updated_at

    def test_user_relationship(self):
        """Test vendor user relationship works correctly."""
        vendor = VendorFactory()
        assert vendor.user
        assert vendor.user.id

        # Test cascade deletion
        user_id = vendor.user.id
        vendor.user.delete()
        assert not Vendor.objects.filter(user_id=user_id).exists()

    def test_location_relationships(self):
        """Test vendor location relationships work correctly."""
        vendor = VendorFactory()
        assert vendor.province.name
        assert vendor.city.name
        assert vendor.district.name
        assert vendor.city.province == vendor.province
        assert vendor.district.city == vendor.city

    def test_vendor_default_values(self):
        """Test vendor model default values."""
        vendor = VendorFactory()
        assert vendor.review_status == Vendor.PENDING
        assert vendor.review_notes == ""
