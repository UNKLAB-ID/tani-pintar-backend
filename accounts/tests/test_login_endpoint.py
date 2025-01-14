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
            username="arter@mail.com",
            email="arter@mail.com",
        )
        profile = Profile.objects.create(user=user, email=user.email)
        profile.generate_login_code()
        return profile

    def test_login(self):
        self.client.post(reverse("accounts:login"), data={"email": self.profile.email})
        login_code = LoginCode.objects.filter(user=self.profile.user).last()

        data = {"email": self.profile.email, "code": login_code.code}

        response = self.client.post(
            reverse("accounts:confirm-login"),
            data=data,
        )

        assert response.json().get("access") is not None
