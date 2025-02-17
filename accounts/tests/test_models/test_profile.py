from django.test import TestCase

from accounts.tests.factories import ProfileFactory


class ProfileModelTest(TestCase):
    def setUp(self):
        self.profile_1 = ProfileFactory()
        self.profile_2 = ProfileFactory()
        self.profile_3 = ProfileFactory()
        self.profile_4 = ProfileFactory()
        self.profile_5 = ProfileFactory()

    def test_get_profile_data(self):
        assert all(
            [
                self.profile_1,
                self.profile_1.user,
                self.profile_1.full_name,
                self.profile_1.headline == "",
                self.profile_1.email,
                self.profile_1.phone_number,
                self.profile_1.profile_type,
                self.profile_1.id_card_file,
                self.profile_1.id_card_validation_status,
            ],
        )
