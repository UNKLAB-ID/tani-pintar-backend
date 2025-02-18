from django.test import TestCase

from accounts.models import LoginCode
from accounts.models import Profile
from accounts.models import VerificationCode
from accounts.tests.factories import ProfileFactory


class ProfileModelTest(TestCase):
    def setUp(self):
        self.profile_1: Profile = ProfileFactory()
        self.profile_2: Profile = ProfileFactory(headline="Kaguya Shinomiya ( •̀ ω •́ )✧")
        self.profile_3: Profile = ProfileFactory()
        self.profile_4: Profile = ProfileFactory()
        self.profile_5: Profile = ProfileFactory()

    def test_get_profile_data(self):
        assert all(
            [
                self.profile_1,
                self.profile_1.user,
                self.profile_1.full_name,
                self.profile_1.headline,
                self.profile_1.email,
                self.profile_1.phone_number,
                self.profile_1.profile_type,
                self.profile_1.id_card_file,
                self.profile_1.id_card_validation_status,
            ],
        )
        assert all(
            [
                self.profile_2,
                self.profile_2.user,
                self.profile_2.full_name,
                self.profile_2.headline == "Kaguya Shinomiya ( •̀ ω •́ )✧",
                self.profile_2.email,
                self.profile_2.phone_number,
                self.profile_2.profile_type,
                self.profile_2.id_card_file,
                self.profile_2.id_card_validation_status,
            ],
        )

    def test_generate_verification_code(self):
        # Check if the verification code is exist
        is_verification_code_exist = VerificationCode.objects.filter(
            user=self.profile_1.user,
        ).exists()
        assert not is_verification_code_exist, "Should return `false`"

        # Generate verification code
        self.profile_1.generate_verification_code()

        # Check if the verification code is exist
        is_verification_code_exist = VerificationCode.objects.filter(
            user=self.profile_1.user,
        ).exists()
        assert is_verification_code_exist, "Should return `true`"

    def test_generate_login_code(self):
        # Check if login code exist
        is_login_code_exist = LoginCode.objects.filter(
            user=self.profile_1.user,
        ).exists()
        assert not is_login_code_exist, "Should return `false`"

        # Generate login code
        self.profile_1.generate_login_code()

        # Check if login code exist
        is_login_code_exist = LoginCode.objects.filter(
            user=self.profile_1.user,
        ).exists()
        assert is_login_code_exist, "Should return `true`"

    def test_follow_user(self):
        # Follow another profile using profile_1
        self.profile_1.follow(self.profile_2)
        self.profile_1.follow(self.profile_3)
        self.profile_1.follow(self.profile_4)
        self.profile_1.follow(self.profile_5)

        # Get following count
        assert (
            self.profile_1.get_following_count() == 4  # noqa: PLR2004
        ), "Profile should have to follow 4 accounts"

        # Get follower count
        assert (
            self.profile_1.get_followers_count() == 0
        ), "Profile should have 0 follower"

        # Create 4 followers for profile_1
        self.profile_2.follow(self.profile_1)
        self.profile_3.follow(self.profile_1)
        self.profile_4.follow(self.profile_1)
        self.profile_5.follow(self.profile_1)

        # Get profile_1 follower count
        assert (
            self.profile_1.get_followers_count() == 4  # noqa: PLR2004
        ), "Profile should have 4 followers"

        # Test unfollow
        assert self.profile_1.is_following(
            self.profile_2,
        ), "`profile_1` should have to follow `profile_2"
        self.profile_1.unfollow(self.profile_2)
        assert not self.profile_1.is_following(
            self.profile_2,
        ), "`profile_1` should have to follow `profile_2"
