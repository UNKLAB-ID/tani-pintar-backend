from django.db import models

from core.users.models import User
from location.models import City
from location.models import District
from location.models import Province


class Vendor(models.Model):
    # Vendor type constants and choices
    TYPE_INDIVIDUAL = "INDIVIDUAL"
    TYPE_COMPANY = "COMPANY"
    TYPE_CHOICES = [
        (TYPE_INDIVIDUAL, "Individual"),
        (TYPE_COMPANY, "Company"),
    ]

    # Review status constants and choices
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"
    STATUS_RESUBMISSION = "RESUBMISSION"
    REVIEW_STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_RESUBMISSION, "Resubmission"),
    ]

    # Core vendor information
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The user account associated with this vendor",
    )
    vendor_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default=TYPE_INDIVIDUAL,
        help_text="Type of vendor: individual person or registered company",
    )
    phone_number = models.CharField(
        max_length=20,
        help_text="Contact phone number for the vendor",
    )
    name = models.CharField(
        max_length=255,
        help_text="Display name for the store or business",
    )

    # Individual vendor specific fields (required only for individual vendors)
    full_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Full legal name of individual vendor",
    )
    id_card_photo = models.ImageField(
        upload_to="vendors/individual/",
        blank=True,
        help_text="Photo of government ID card for verification",
    )
    logo = models.ImageField(
        upload_to="vendors/logos/",
        blank=True,
        help_text="Vendor logo image",
    )

    # Company vendor specific fields (required only for company vendors)
    business_number = models.CharField(
        max_length=255,
        blank=True,
        help_text="Official business registration number",
    )
    business_nib_file = models.FileField(
        upload_to="vendors/company/nib/",
        blank=True,
        help_text="NIB (Business Identification Number) document",
    )
    npwp_number = models.CharField(
        max_length=255,
        blank=True,
        help_text="NPWP (Taxpayer Registration Number)",
    )
    npwp_file = models.FileField(
        max_length=255,
        blank=True,
        help_text="NPWP (Taxpayer Registration Number) file",
    )

    # Location information
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="vendors",
        help_text="Province where the vendor is located",
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="vendors",
        help_text="City where the vendor is located",
    )
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name="vendors",
        help_text="District/subdistrict where the vendor is located",
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=False,
        help_text="GPS latitude coordinate",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=False,
        help_text="GPS longitude coordinate",
    )
    address_detail = models.CharField(
        max_length=255,
        null=False,
        help_text="Detailed address information",
    )
    postal_code = models.CharField(
        max_length=20,
        null=False,
        help_text="Postal/ZIP code",
    )

    # Review and approval workflow
    review_status = models.CharField(
        choices=REVIEW_STATUS_CHOICES,
        default=STATUS_PENDING,
        max_length=25,
        help_text="Current status in the vendor approval process",
    )
    review_notes = models.TextField(
        blank=True,
        help_text="Admin notes and feedback for the review process",
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the vendor record was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the vendor record was last updated",
    )

    class Meta:
        indexes = [
            models.Index(fields=["vendor_type", "review_status"]),
            models.Index(fields=["user"]),
            models.Index(fields=["province", "city", "district"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_vendor_type_display()})"
