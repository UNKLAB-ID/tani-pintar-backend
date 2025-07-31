import requests
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string

from accounts import tasks
from core.users.models import User
from location.models import City
from location.models import Country


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
    about = models.TextField(max_length=500, default="", blank=True)
    headline = models.CharField(max_length=255, default="", blank=True)
    farmer_community = models.CharField(max_length=255, default="", blank=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    city = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    email = models.EmailField(unique=True, max_length=255, blank=False)
    phone_number = models.CharField(max_length=20, unique=True, blank=False)
    profile_type = models.CharField(
        choices=PROFILE_TYPE_CHOICES,
        default=FARMER,
        max_length=25,
    )

    profile_picture_url = models.ImageField(upload_to="profile-pictures", blank=True)
    thumbnail_profile_picture_url = models.ImageField(
        upload_to="thumbnail-pictures",
        blank=True,
    )
    cover_picture_url = models.ImageField(upload_to="cover-pictures", blank=True)

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

    def generate_verification_code(self):
        verification_code = VerificationCode.objects.create(user=self.user)
        tasks.send_verification_code.delay(verification_code.id)

    def generate_login_code(self):
        login_code = LoginCode.objects.create(user=self.user)
        tasks.send_login_code.delay(login_code.id)

    def follow(self, profile_to_follow):
        if self != profile_to_follow:
            Follow.objects.get_or_create(follower=self, following=profile_to_follow)

    def unfollow(self, profile_to_unfollow):
        Follow.objects.filter(follower=self, following=profile_to_unfollow).delete()

    def is_following(self, profile):
        return self.following.filter(following=profile).exists()

    def get_followers_count(self):
        return self.followers.count()

    def get_following_count(self):
        return self.following.count()

    def are_friends(self, other_profile):
        """
        Check if this profile and another profile are friends (mutual followers)
        """
        if self == other_profile:
            return False
        # Check if both follow each other (mutual followers = friends)
        return (
            Follow.objects.filter(follower=self, following=other_profile).exists()
            and Follow.objects.filter(follower=other_profile, following=self).exists()
        )


class Follow(models.Model):
    follower = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="following",  # Profile.following.all() gets all profiles user follows  # noqa: E501
    )
    following = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="followers",  # Profile.followers.all() gets all followers of profile  # noqa: E501
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")  # Prevent duplicate follows
        # Ensure user can't follow themselves
        constraints = [
            models.CheckConstraint(
                check=~models.Q(follower=models.F("following")),
                name="cannot_follow_self",
            ),
        ]

    def __str__(self):
        return f"{self.follower.full_name} follows {self.following.full_name}"


class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)

    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(blank=True)

    def __str__(self):
        return f"{self.user} | {self.code} | {self.expired_at}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_expired_at()

        if not self.code:
            self.code = get_random_string(length=4, allowed_chars="0123456789")

        return super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.expired_at < timezone.localtime()

    def create_expired_at(self):
        self.expired_at = timezone.localtime() + timezone.timedelta(minutes=30)

    def send_discord_webhook_notification(self) -> bool:
        webhook_url = settings.REGISTRATION_CODE_DISCORD_WEBHOOK_URL
        embed = {
            "title": "Verification Code Notification",
            "description": f"Registration code for: **{self.user.username}**",
            "fields": [
                {
                    "name": "Verification Code",
                    "value": f"`{self.code}`",
                    "inline": False,
                },
            ],
            "color": 0x7289DA,
        }

        payload = {"embeds": [embed]}
        response = requests.post(webhook_url, json=payload, timeout=10)

        return response.ok


class LoginCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=4)

    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(blank=True)

    def __str__(self):
        return f"{self.user} | {self.code}"

    def save(self, *args, **kwargs):
        if not self.id:
            self.create_expired_at()

        if not self.code:
            self.code = get_random_string(length=4, allowed_chars="0123456789")

        return super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.expired_at < timezone.localtime()

    def create_expired_at(self):
        self.expired_at = timezone.localtime() + timezone.timedelta(minutes=10)

    def send_discord_webhook_notification(self) -> bool:
        webhook_url = settings.LOGIN_CODE_DISCORD_WEBHOOK_URL
        embed = {
            "title": "Login Code Notification",
            "description": f"Login code for: **{self.user.username}**",
            "fields": [
                {
                    "name": "Login Code",
                    "value": f"`{self.code}`",
                    "inline": False,
                },
            ],
            "color": 0x7289DA,
        }

        payload = {"embeds": [embed]}
        response = requests.post(webhook_url, json=payload, timeout=10)

        return response.ok
