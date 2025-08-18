from django.core.exceptions import ValidationError
from django.db import models

from vendors.mixins import BaseVendorModel
from vendors.mixins import LocationMixin


class Vendor(BaseVendorModel, LocationMixin):
    vendor_type = models.CharField(
        max_length=10,
        choices=BaseVendorModel.TYPE_CHOICES,
        default=BaseVendorModel.TYPE_INDIVIDUAL,
    )

    # Individual vendor fields (optional for companies)
    full_name = models.CharField(max_length=255, blank=True)
    id_card_photo = models.ImageField(upload_to="vendors/individual/", blank=True)

    # Company vendor fields (optional for individuals)
    business_name = models.CharField(max_length=255, blank=True)
    business_number = models.CharField(max_length=255, blank=True)
    business_nib = models.ImageField(upload_to="vendors/company/nib/", blank=True)
    npwp = models.CharField(max_length=255, blank=True)

    # Unified common fields
    name = models.CharField(max_length=255)  # store_name or business display name
    logo = models.ImageField(upload_to="vendors/logos/", blank=True)
    address = models.CharField(max_length=255)  # store/office address

    def __str__(self):
        return f"{self.name} ({self.get_vendor_type_display()})"

    def clean(self):
        super().clean()

        # Validate location hierarchy relationships
        if self.city and self.province and self.city.province != self.province:
            raise ValidationError(
                {"city": "City must belong to the selected province."},
            )

        if self.district and self.city and self.district.city != self.city:
            raise ValidationError(
                {"district": "District must belong to the selected city."},
            )

        if self.vendor_type == self.TYPE_INDIVIDUAL:
            self._validate_individual_vendor()
        elif self.vendor_type == self.TYPE_COMPANY:
            self._validate_company_vendor()

    def _validate_individual_vendor(self):
        """Validate required fields for individual vendors."""
        if not self.full_name:
            raise ValidationError(
                {"full_name": "Full name is required for individual vendors."},
            )
        if not self.id_card_photo:
            raise ValidationError(
                {"id_card_photo": "ID card photo is required for individual vendors."},
            )

    def _validate_company_vendor(self):
        """Validate required fields for company vendors."""
        if not self.business_name:
            raise ValidationError(
                {"business_name": "Business name is required for company vendors."},
            )
        if not self.business_number:
            raise ValidationError(
                {"business_number": "Business number is required for company vendors."},
            )
        if not self.npwp:
            raise ValidationError({"npwp": "NPWP is required for company vendors."})

    class Meta:
        indexes = [
            models.Index(fields=["vendor_type", "review_status"]),
            models.Index(fields=["user"]),
            models.Index(fields=["province", "city", "district"]),
        ]
