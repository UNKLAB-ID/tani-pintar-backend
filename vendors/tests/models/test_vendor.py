import time
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from vendors.models import Vendor
from vendors.tests.factories import CompanyVendorFactory
from vendors.tests.factories import IndividualVendorFactory


class IndividualVendorCreationTest(TestCase):
    """Test creating individual vendor model."""

    fixtures = ["initial_data.json"]

    def test_create_individual_vendor(self):
        """Test creating an individual vendor with all required fields."""
        vendor = IndividualVendorFactory()

        # Verify vendor is saved to database
        assert vendor.id is not None
        assert Vendor.objects.filter(id=vendor.id).exists()

        # Verify vendor type
        assert vendor.vendor_type == Vendor.TYPE_INDIVIDUAL
        assert vendor.get_vendor_type_display() == "Individual"

        # Verify individual-specific required fields
        assert vendor.full_name != ""
        assert vendor.id_card_photo is not None

        # Verify common required fields
        assert vendor.user is not None
        assert vendor.name != ""
        assert vendor.phone_number != ""

        # Verify location fields
        assert vendor.province is not None
        assert vendor.city is not None
        assert vendor.district is not None
        assert vendor.latitude is not None
        assert vendor.longitude is not None
        assert vendor.address_detail != ""
        assert vendor.postal_code != ""

        # Verify default status
        assert vendor.review_status == Vendor.STATUS_PENDING

        # Verify company fields are empty for individual vendor
        assert vendor.business_number == ""
        assert (
            vendor.business_nib_file.name is None or vendor.business_nib_file.name == ""
        )
        assert vendor.npwp_number == ""


class CompanyVendorCreationTest(TestCase):
    """Test creating company vendor model."""

    fixtures = ["initial_data.json"]

    def test_create_company_vendor(self):
        """Test creating a company vendor with all required fields."""
        vendor = CompanyVendorFactory()

        # Verify vendor is saved to database
        assert vendor.id is not None
        assert Vendor.objects.filter(id=vendor.id).exists()

        # Verify vendor type
        assert vendor.vendor_type == Vendor.TYPE_COMPANY
        assert vendor.get_vendor_type_display() == "Company"

        # Verify company-specific required fields
        assert vendor.business_number != ""
        assert vendor.business_nib_file is not None
        assert vendor.npwp_number != ""
        assert vendor.npwp_file is not None

        # Verify common required fields
        assert vendor.user is not None
        assert vendor.name != ""
        assert vendor.phone_number != ""

        # Verify location fields
        assert vendor.province is not None
        assert vendor.city is not None
        assert vendor.district is not None
        assert vendor.latitude is not None
        assert vendor.longitude is not None
        assert vendor.address_detail != ""
        assert vendor.postal_code != ""

        # Verify default status
        assert vendor.review_status == Vendor.STATUS_PENDING

        # Verify individual fields are empty for company vendor
        assert vendor.full_name == ""
        assert vendor.id_card_photo.name is None or vendor.id_card_photo.name == ""


class IndividualVendorValidationTest(TestCase):
    """Test validation logic for individual vendors."""

    fixtures = ["initial_data.json"]

    def test_missing_full_name_raises_validation_error(self):
        """Test that individual vendor without full_name fails validation."""
        vendor = IndividualVendorFactory.build(full_name="")

        with pytest.raises(ValidationError) as exc_info:
            vendor.full_clean()

        assert "full_name" in exc_info.value.error_dict
        assert (
            "Full name is required for individual vendors."
            in exc_info.value.error_dict["full_name"][0]
        )

    def test_missing_id_card_photo_raises_validation_error(self):
        """Test that individual vendor without id_card_photo fails validation."""
        vendor = IndividualVendorFactory.build(id_card_photo=None)

        with pytest.raises(ValidationError) as exc_info:
            vendor.full_clean()

        assert "id_card_photo" in exc_info.value.error_dict
        assert (
            "ID card photo is required for individual vendors."
            in exc_info.value.error_dict["id_card_photo"][0]
        )

    def test_missing_both_fields_raises_multiple_errors(self):
        """Test that missing multiple fields raises all validation errors."""
        vendor = IndividualVendorFactory.build(full_name="", id_card_photo=None)

        with pytest.raises(ValidationError) as exc_info:
            vendor.full_clean()

        assert "full_name" in exc_info.value.error_dict
        assert "id_card_photo" in exc_info.value.error_dict

    def test_valid_individual_vendor_passes_validation(self):
        """Test that a valid individual vendor passes validation."""
        vendor = IndividualVendorFactory()

        # Should not raise any exception
        vendor.full_clean()


class CompanyVendorValidationTest(TestCase):
    """Test validation logic for company vendors."""

    fixtures = ["initial_data.json"]

    def test_missing_business_number_raises_validation_error(self):
        """Test that company vendor without business_number fails validation."""
        vendor = CompanyVendorFactory.build(business_number="")

        with pytest.raises(ValidationError) as exc_info:
            vendor.full_clean()

        assert "business_number" in exc_info.value.error_dict
        assert (
            "Business number is required for company vendors."
            in exc_info.value.error_dict["business_number"][0]
        )

    def test_missing_business_nib_file_raises_validation_error(self):
        """Test company vendor without business_nib_file fails validation."""
        vendor = CompanyVendorFactory.build(business_nib_file=None)

        with pytest.raises(ValidationError) as exc_info:
            vendor.full_clean()

        assert "business_nib_file" in exc_info.value.error_dict
        assert (
            "NIB file is required for company vendors."
            in exc_info.value.error_dict["business_nib_file"][0]
        )

    def test_missing_npwp_number_raises_validation_error(self):
        """Test that company vendor without npwp_number fails validation."""
        vendor = CompanyVendorFactory.build(npwp_number="")

        with pytest.raises(ValidationError) as exc_info:
            vendor.full_clean()

        assert "npwp_number" in exc_info.value.error_dict
        assert (
            "NPWP number is required for company vendors."
            in exc_info.value.error_dict["npwp_number"][0]
        )

    def test_missing_npwp_file_raises_validation_error(self):
        """Test that company vendor without npwp_file fails validation."""
        vendor = CompanyVendorFactory.build(npwp_file=None)

        with pytest.raises(ValidationError) as exc_info:
            vendor.full_clean()

        assert "npwp_file" in exc_info.value.error_dict
        assert (
            "NPWP file is required for company vendors."
            in exc_info.value.error_dict["npwp_file"][0]
        )

    def test_missing_all_company_fields_raises_multiple_errors(self):
        """Test that missing all company fields raises all validation errors."""
        vendor = CompanyVendorFactory.build(
            business_number="",
            business_nib_file=None,
            npwp_number="",
            npwp_file=None,
        )

        with pytest.raises(ValidationError) as exc_info:
            vendor.full_clean()

        assert "business_number" in exc_info.value.error_dict
        assert "business_nib_file" in exc_info.value.error_dict
        assert "npwp_number" in exc_info.value.error_dict
        assert "npwp_file" in exc_info.value.error_dict

    def test_valid_company_vendor_passes_validation(self):
        """Test that a valid company vendor passes validation."""
        vendor = CompanyVendorFactory()

        # Should not raise any exception
        vendor.full_clean()


class VendorReviewStatusTest(TestCase):
    """Test review status workflow and transitions."""

    fixtures = ["initial_data.json"]

    def test_default_status_is_pending(self):
        """Test that newly created vendors have PENDING status."""
        vendor = IndividualVendorFactory()
        assert vendor.review_status == Vendor.STATUS_PENDING

    def test_status_transition_to_approved(self):
        """Test transitioning vendor status to APPROVED."""
        vendor = IndividualVendorFactory()
        vendor.review_status = Vendor.STATUS_APPROVED
        vendor.save()

        vendor.refresh_from_db()
        assert vendor.review_status == Vendor.STATUS_APPROVED
        assert vendor.get_review_status_display() == "Approved"

    def test_status_transition_to_rejected(self):
        """Test transitioning vendor status to REJECTED."""
        vendor = IndividualVendorFactory()
        vendor.review_status = Vendor.STATUS_REJECTED
        vendor.review_notes = "Missing required documentation"
        vendor.save()

        vendor.refresh_from_db()
        assert vendor.review_status == Vendor.STATUS_REJECTED
        assert vendor.get_review_status_display() == "Rejected"
        assert vendor.review_notes == "Missing required documentation"

    def test_status_transition_to_resubmission(self):
        """Test transitioning vendor status to RESUBMISSION."""
        vendor = IndividualVendorFactory(review_status=Vendor.STATUS_REJECTED)
        vendor.review_status = Vendor.STATUS_RESUBMISSION
        vendor.save()

        vendor.refresh_from_db()
        assert vendor.review_status == Vendor.STATUS_RESUBMISSION
        assert vendor.get_review_status_display() == "Resubmission"

    def test_all_status_choices_display_correctly(self):
        """Test that all status choices have correct display values."""
        status_mapping = {
            Vendor.STATUS_PENDING: "Pending",
            Vendor.STATUS_APPROVED: "Approved",
            Vendor.STATUS_REJECTED: "Rejected",
            Vendor.STATUS_RESUBMISSION: "Resubmission",
        }

        for status, display in status_mapping.items():
            vendor = IndividualVendorFactory(review_status=status)
            assert vendor.get_review_status_display() == display

    def test_review_notes_can_be_updated(self):
        """Test that review_notes can be added and updated."""
        vendor = IndividualVendorFactory()
        assert vendor.review_notes == ""

        vendor.review_notes = "Please update your ID card photo"
        vendor.save()

        vendor.refresh_from_db()
        assert vendor.review_notes == "Please update your ID card photo"


class VendorLocationRelationshipTest(TestCase):
    """Test location relationships and constraints."""

    fixtures = ["initial_data.json"]

    def test_city_belongs_to_province(self):
        """Test that vendor's city belongs to its province."""
        vendor = IndividualVendorFactory()

        assert vendor.city.province == vendor.province

    def test_district_belongs_to_city(self):
        """Test that vendor's district belongs to its city."""
        vendor = IndividualVendorFactory()

        assert vendor.district.city == vendor.city

    def test_complete_location_hierarchy(self):
        """Test the complete location hierarchy is consistent."""
        vendor = IndividualVendorFactory()

        # District -> City -> Province should be consistent
        assert vendor.district.city == vendor.city
        assert vendor.city.province == vendor.province

    def test_vendors_related_name_on_province(self):
        """Test the 'vendors' related name on Province."""
        vendor = IndividualVendorFactory()
        vendors_in_province = vendor.province.vendors.all()

        assert vendor in vendors_in_province

    def test_vendors_related_name_on_city(self):
        """Test the 'vendors' related name on City."""
        vendor = IndividualVendorFactory()
        vendors_in_city = vendor.city.vendors.all()

        assert vendor in vendors_in_city

    def test_vendors_related_name_on_district(self):
        """Test the 'vendors' related name on District."""
        vendor = IndividualVendorFactory()
        vendors_in_district = vendor.district.vendors.all()

        assert vendor in vendors_in_district

    def test_query_vendors_by_location(self):
        """Test querying vendors by different location levels."""
        vendor1 = IndividualVendorFactory()
        vendor2 = IndividualVendorFactory()

        # Query by province
        province_vendors = Vendor.objects.filter(province=vendor1.province)
        assert vendor1 in province_vendors

        # Query by city
        city_vendors = Vendor.objects.filter(city=vendor2.city)
        assert vendor2 in city_vendors

        # Query by district
        district_vendors = Vendor.objects.filter(district=vendor1.district)
        assert vendor1 in district_vendors

    def test_cascade_delete_province(self):
        """Test that deleting province cascades to vendors."""
        vendor = IndividualVendorFactory()
        vendor_id = vendor.id
        province = vendor.province

        province.delete()

        assert not Vendor.objects.filter(id=vendor_id).exists()

    def test_cascade_delete_city(self):
        """Test that deleting city cascades to vendors."""
        vendor = IndividualVendorFactory()
        vendor_id = vendor.id
        city = vendor.city

        city.delete()

        assert not Vendor.objects.filter(id=vendor_id).exists()

    def test_cascade_delete_district(self):
        """Test that deleting district cascades to vendors."""
        vendor = IndividualVendorFactory()
        vendor_id = vendor.id
        district = vendor.district

        district.delete()

        assert not Vendor.objects.filter(id=vendor_id).exists()


class VendorUserRelationshipTest(TestCase):
    """Test user relationships and constraints."""

    fixtures = ["initial_data.json"]

    def test_vendor_has_user(self):
        """Test that vendor is associated with a user."""
        vendor = IndividualVendorFactory()

        assert vendor.user is not None
        assert vendor.user.id is not None

    def test_cascade_delete_user(self):
        """Test that deleting user cascades to vendors."""
        vendor = IndividualVendorFactory()
        vendor_id = vendor.id
        user = vendor.user

        user.delete()

        assert not Vendor.objects.filter(id=vendor_id).exists()

    def test_multiple_vendors_for_same_user(self):
        """Test that same user can have multiple vendors."""
        vendor1 = IndividualVendorFactory()
        vendor2 = CompanyVendorFactory(user=vendor1.user)

        assert vendor1.user == vendor2.user
        assert vendor1.id != vendor2.id

        user_vendors = Vendor.objects.filter(user=vendor1.user)
        assert len(user_vendors) == 2  # noqa: PLR2004
        assert vendor1 in user_vendors
        assert vendor2 in user_vendors

    def test_vendor_cannot_exist_without_user(self):
        """Test that vendor requires a user."""
        # Create a vendor and then try to set user to None
        vendor = IndividualVendorFactory()
        vendor.user = None

        with pytest.raises(IntegrityError):
            vendor.save()


class VendorFieldConstraintsTest(TestCase):
    """Test field constraints and validations."""

    fixtures = ["initial_data.json"]

    def test_latitude_precision(self):
        """Test latitude field precision (9 digits, 6 decimal places)."""
        vendor = IndividualVendorFactory(latitude=Decimal("-6.175110"))

        assert vendor.latitude == Decimal("-6.175110")
        assert isinstance(vendor.latitude, Decimal)

    def test_longitude_precision(self):
        """Test longitude field precision (9 digits, 6 decimal places)."""
        vendor = IndividualVendorFactory(longitude=Decimal("106.865039"))

        assert vendor.longitude == Decimal("106.865039")
        assert isinstance(vendor.longitude, Decimal)

    def test_phone_number_max_length(self):
        """Test phone_number field respects max length."""
        long_phone = "0" * 20  # Max length is 20
        vendor = IndividualVendorFactory(phone_number=long_phone)

        assert len(vendor.phone_number) <= 20  # noqa: PLR2004

    def test_address_detail_max_length(self):
        """Test address_detail field respects max length."""
        long_address = "A" * 255  # Max length is 255
        vendor = IndividualVendorFactory(address_detail=long_address)

        assert len(vendor.address_detail) <= 255  # noqa: PLR2004

    def test_postal_code_max_length(self):
        """Test postal_code field respects max length."""
        postal_code = "12345678901234567890"  # 20 chars (max length)
        vendor = IndividualVendorFactory(postal_code=postal_code)

        assert len(vendor.postal_code) <= 20  # noqa: PLR2004

    def test_vendor_type_choices(self):
        """Test that vendor_type only accepts valid choices."""
        individual = IndividualVendorFactory()
        company = CompanyVendorFactory()

        assert individual.vendor_type in [choice[0] for choice in Vendor.TYPE_CHOICES]
        assert company.vendor_type in [choice[0] for choice in Vendor.TYPE_CHOICES]


class VendorStringRepresentationTest(TestCase):
    """Test string representation of vendors."""

    fixtures = ["initial_data.json"]

    def test_individual_vendor_str(self):
        """Test string representation of individual vendor."""
        vendor = IndividualVendorFactory(name="John's Farm Store")

        expected = "John's Farm Store (Individual)"
        assert str(vendor) == expected

    def test_company_vendor_str(self):
        """Test string representation of company vendor."""
        vendor = CompanyVendorFactory(name="AgriTech Solutions Ltd")

        expected = "AgriTech Solutions Ltd (Company)"
        assert str(vendor) == expected

    def test_vendor_str_with_special_characters(self):
        """Test string representation with special characters in name."""
        vendor = IndividualVendorFactory(name="Toko Tani & Berkah 123")

        expected = "Toko Tani & Berkah 123 (Individual)"
        assert str(vendor) == expected


class VendorTimestampTest(TestCase):
    """Test timestamp behavior (created_at, updated_at)."""

    fixtures = ["initial_data.json"]

    def test_created_at_auto_generated(self):
        """Test that created_at is automatically set on creation."""
        before_creation = timezone.now()
        vendor = IndividualVendorFactory()
        after_creation = timezone.now()

        assert vendor.created_at is not None
        assert before_creation <= vendor.created_at <= after_creation

    def test_updated_at_auto_generated(self):
        """Test that updated_at is automatically set on creation."""
        before_creation = timezone.now()
        vendor = IndividualVendorFactory()
        after_creation = timezone.now()

        assert vendor.updated_at is not None
        assert before_creation <= vendor.updated_at <= after_creation

    def test_updated_at_changes_on_modification(self):
        """Test that updated_at changes when vendor is modified."""
        vendor = IndividualVendorFactory()
        original_updated_at = vendor.updated_at

        # Wait a small amount to ensure time difference
        time.sleep(0.01)

        vendor.name = "Updated Store Name"
        vendor.save()

        vendor.refresh_from_db()
        assert vendor.updated_at > original_updated_at

    def test_created_at_does_not_change_on_update(self):
        """Test that created_at doesn't change when vendor is updated."""
        vendor = IndividualVendorFactory()
        original_created_at = vendor.created_at

        time.sleep(0.01)

        vendor.name = "Updated Store Name"
        vendor.save()

        vendor.refresh_from_db()
        assert vendor.created_at == original_created_at


class VendorHistoricalRecordsTest(TestCase):
    """Test historical records tracking."""

    fixtures = ["initial_data.json"]

    def test_history_created_on_vendor_creation(self):
        """Test that history record is created when vendor is created."""
        vendor = IndividualVendorFactory()

        # Check that historical record exists
        assert vendor.history.count() == 1

        # Get the historical record
        history = vendor.history.first()
        assert history.name == vendor.name
        assert history.vendor_type == vendor.vendor_type

    def test_history_tracks_changes(self):
        """Test that history tracks changes to vendor."""
        vendor = IndividualVendorFactory(name="Original Name")
        original_history_count = vendor.history.count()

        # Update the vendor
        vendor.name = "Updated Name"
        vendor.save()

        # Check that new history record was created
        assert vendor.history.count() == original_history_count + 1

        # Verify the history records
        latest_history = vendor.history.first()
        assert latest_history.name == "Updated Name"

        oldest_history = vendor.history.last()
        assert oldest_history.name == "Original Name"

    def test_history_tracks_status_changes(self):
        """Test that history tracks review status changes."""
        vendor = IndividualVendorFactory(review_status=Vendor.STATUS_PENDING)

        vendor.review_status = Vendor.STATUS_APPROVED
        vendor.review_notes = "All documents verified"
        vendor.save()

        # Get history records
        current_history = vendor.history.first()
        previous_history = vendor.history.all()[1]

        assert current_history.review_status == Vendor.STATUS_APPROVED
        assert previous_history.review_status == Vendor.STATUS_PENDING


class VendorModelMetaTest(TestCase):
    """Test model meta configuration."""

    fixtures = ["initial_data.json"]

    def test_model_has_indexes(self):
        """Test that model has configured indexes."""
        # Check that indexes are defined on the model
        meta = Vendor._meta  # noqa: SLF001
        assert len(meta.indexes) > 0

    def test_query_by_vendor_type_and_status(self):
        """Test querying with indexed fields (vendor_type, review_status)."""
        # Create vendors with different types and statuses
        IndividualVendorFactory(review_status=Vendor.STATUS_PENDING)
        IndividualVendorFactory(review_status=Vendor.STATUS_APPROVED)
        CompanyVendorFactory(review_status=Vendor.STATUS_PENDING)

        # Query using indexed fields
        pending_individuals = Vendor.objects.filter(
            vendor_type=Vendor.TYPE_INDIVIDUAL,
            review_status=Vendor.STATUS_PENDING,
        )

        assert pending_individuals.count() == 1
        assert pending_individuals.first().vendor_type == Vendor.TYPE_INDIVIDUAL
        assert pending_individuals.first().review_status == Vendor.STATUS_PENDING

    def test_query_by_user(self):
        """Test querying with indexed user field."""
        vendor = IndividualVendorFactory()

        # Query by user (indexed field)
        user_vendors = Vendor.objects.filter(user=vendor.user)

        assert vendor in user_vendors

    def test_query_by_location(self):
        """Test querying with indexed location fields."""
        vendor = IndividualVendorFactory()

        # Query by province, city, district (composite index)
        location_vendors = Vendor.objects.filter(
            province=vendor.province,
            city=vendor.city,
            district=vendor.district,
        )

        assert vendor in location_vendors
