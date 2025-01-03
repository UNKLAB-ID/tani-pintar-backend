from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from accounts.models import Profile
from accounts.models import VerificationCode
from core.users.models import User


class RegisterTests(TestCase):
    def setUp(self):
        self.url = reverse("accounts:register")

    def test_register_success(self):
        id_card = SimpleUploadedFile(
            "test_id_card.jpg",
            b"dummy image content",
            content_type="image/jpeg",
        )

        data = {
            "name": "Arter Tendean",
            "email": "arter@animemoe.us",
            "phone_number": "123456789",
            "id_card_file": id_card,
            "password": "Password123!",
        }

        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert (
            User.objects.filter(username=data.get("email")).exists() is True
        ), "User should be created"
        assert (
            Profile.objects.filter(email=data.get("email")).exists() is True
        ), "Profile should be created"

    def test_register_duplicate_email(self):
        self.test_register_success()

        id_card = SimpleUploadedFile(
            "test_id_card.jpg",
            b"dummy image content",
            content_type="image/jpeg",
        )

        data = {
            "name": "Arter Tendean",
            "email": "arter@animemoe.us",
            "phone_number": "123456789",
            "id_card_file": id_card,
            "password": "Password123!",
        }

        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json().get("email")[0] == "Email already exists"

    def test_register_confirmation(self):
        self.test_register_success()

        verification_code = VerificationCode.objects.filter(
            user__username="arter@animemoe.us",
        ).last()
        assert verification_code is not None, "Verification code should be created"

        data = {"email": "arter@animemoe.us", "code": verification_code.code}
        response = self.client.post(
            reverse("accounts:confirm-registration"),
            data,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        user = User.objects.get(username=data.get("email"))
        assert user.is_active is True, "User should be activated"
