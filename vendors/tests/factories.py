import factory
from faker import Faker

from core.users.tests.factories import UserFactory
from location.tests.factories import CityFactory
from location.tests.factories import DistrictFactory
from location.tests.factories import ProvinceFactory
from vendors.models import Vendor

fake = Faker()


class VendorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vendor

    user = factory.SubFactory(UserFactory)
    vendor_type = Vendor.TYPE_INDIVIDUAL
    name = factory.Faker("company")
    full_name = factory.Faker("name")  # Required for individual vendors
    id_card_photo = factory.django.ImageField(  # Required for individual vendors
        filename="id_card.jpg",
        size=1024,
    )
    phone_number = factory.Faker("phone_number", locale="id_ID")
    review_status = Vendor.PENDING
    review_notes = ""

    # Location fields with proper relationships
    province = factory.SubFactory(ProvinceFactory)
    city = factory.SubFactory(CityFactory, province=factory.SelfAttribute("..province"))
    district = factory.SubFactory(DistrictFactory, city=factory.SelfAttribute("..city"))
    latitude = factory.Faker("latitude")
    longitude = factory.Faker("longitude")
    address = factory.Faker("address")
    address_detail = factory.Faker("street_address")
    postal_code = factory.Faker("postcode")

    # Optional fields
    logo = factory.django.ImageField(
        filename="vendor_logo.jpg",
        size=1024,
    )


class IndividualVendorFactory(VendorFactory):
    vendor_type = Vendor.TYPE_INDIVIDUAL
    full_name = factory.Faker("name")
    id_card_photo = factory.django.ImageField(
        filename="id_card.jpg",
        size=1024,
    )

    # Clear company fields
    business_name = ""
    business_number = ""
    business_nib = None
    npwp = ""


class CompanyVendorFactory(VendorFactory):
    vendor_type = Vendor.TYPE_COMPANY
    business_name = factory.Faker("company")
    business_number = factory.LazyFunction(lambda: fake.uuid4()[:15])
    business_nib = factory.django.ImageField(
        filename="business_nib.jpg",
        size=1024,
    )
    npwp = factory.LazyFunction(lambda: fake.uuid4()[:15])

    # Clear individual fields
    full_name = ""
    id_card_photo = None
