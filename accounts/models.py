from django.db import models

from core.users.models import User


class Profile(models.Model):
    # Profile Type
    FARMER = "Farmer"
    DISTRIBUTOR = "Distributor"
    CONSUMER = "Consumer"
    SUPPLIER = "Supplier"
    AGENT = "Agent"
    VENDOR = "Vendor"

    PROFILE_TYPE_CHOICES = [
        (FARMER, "Farmer"),
        (DISTRIBUTOR, "Distributor"),
        (CONSUMER, "Consumer"),
        (SUPPLIER, "Supplier"),
        (AGENT, "Agent"),
        (VENDOR, "Vendor"),
    ]

    # ID Card Status
    PENDING = "Pending"
    VERIFIED = "Verified"
    REJECTED = "Rejected"
    RESUBMISSION = "Resubmission"
    EXPIRED = "Expired"
    ID_CARD_STATUS_CHOICES = [
        (PENDING, "Pending"),
        (VERIFIED, "Verified"),
        (REJECTED, "Rejected"),
        (RESUBMISSION, "Resubmission"),
        (EXPIRED, "Expired"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    full_name = models.CharField(max_length=255, blank=False)
    email = models.EmailField(unique=True, max_length=255, blank=False)
    phone_number = models.CharField(max_length=20, unique=True, blank=False)
    profile_type = models.CharField(
        choices=PROFILE_TYPE_CHOICES,
        default=FARMER,
        max_length=25,
    )
    id_card_file = models.FileField(upload_to="id-card-images/")
    id_card_validation_status = models.CharField(
        choices=ID_CARD_STATUS_CHOICES,
        default=PENDING,
        max_length=25,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.full_name} | {self.profile_type} | {self.id_card_validation_status}"
        )
