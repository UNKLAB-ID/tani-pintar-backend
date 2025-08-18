from django.db import models

from core.users.models import User
from location.models import City
from location.models import District
from location.models import Province


class BaseVendorModel(models.Model):
    TYPE_INDIVIDUAL = "individual"
    TYPE_COMPANY = "company"
    TYPE_CHOICES = [
        (TYPE_INDIVIDUAL, "Individual"),
        (TYPE_COMPANY, "Company"),
    ]

    # Review status constants
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    RESUBMISSION = "Resubmission"
    REVIEW_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
        (RESUBMISSION, "Resubmission"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    review_status = models.CharField(
        choices=REVIEW_STATUS_CHOICES,
        default=PENDING,
        max_length=25,
    )
    review_notes = models.TextField(
        blank=True,
        help_text="Admin notes for review process",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LocationMixin(models.Model):
    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="vendors",
    )
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="vendors")
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name="vendors",
    )

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=False)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=False)
    address_detail = models.CharField(max_length=255, null=False)
    postal_code = models.CharField(max_length=20, null=False)

    class Meta:
        abstract = True
