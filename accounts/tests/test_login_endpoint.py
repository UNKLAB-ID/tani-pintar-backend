from django.test import TestCase
from django.urls import reverse

from accounts.models import LoginCode
from accounts.models import Profile
from core.users.models import User


class TestLoginEndpoint(TestCase):
    def setUp(self):
        self.profile = self.create_test_user_profile()

    def create_test_user_profile(self):
        user = User.objects.create_user(
            username="1234567890",
            email="arter@mail.com",
        )
        profile = Profile.objects.create(
            user=user,
            email=user.email,
            phone_number="1234567890",
        )
        profile.generate_login_code()
        return profile

    def test_login(self):
        # Request a login code
        self.client.post(
            reverse("accounts:login"),
            data={"phone_number": self.profile.phone_number},
        )

        # Get the latest login code
        login_code = LoginCode.objects.filter(user=self.profile.user).last()

        # Confirm login with phone number and code
        data = {"phone_number": self.profile.phone_number, "code": login_code.code}
        response = self.client.post(
            reverse("accounts:confirm-login"),
            data=data,
        )

        # Verify that we got an access token
        assert response.json().get("access") is not None
        assert response.json().get("refresh") is not None
