import factory
from faker import Faker

from accounts.models import Profile
from core.users.tests.factories import UserFactory

fake = Faker()


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    full_name = factory.LazyAttribute(lambda o: o.user.username)
    headline = factory.Faker("sentence")
    email = factory.LazyAttribute(lambda o: o.user.email)
    phone_number = factory.Faker("phone_number", locale="id_ID")
    profile_type = Profile.FARMER
    id_card_file = factory.django.FileField(
        filename="id_card_example.jpg",
        size=1024,
    )
    id_card_validation_status = Profile.PENDING
