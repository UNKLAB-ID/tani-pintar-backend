import factory
from faker import Faker

from location.models import City
from location.models import Country
from location.models import District
from location.models import Province

fake = Faker()


class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Country

    name = factory.Faker("country")
    code = factory.LazyFunction(lambda: fake.country_code(representation="alpha-2"))


class ProvinceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Province

    name = factory.Faker("state")
    country = factory.SubFactory(CountryFactory)


class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = City

    name = factory.Faker("city")
    province = factory.SubFactory(ProvinceFactory)


class DistrictFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = District

    name = factory.Faker("city_suffix")
    city = factory.SubFactory(CityFactory)
