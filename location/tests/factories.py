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
        django_get_or_create = ("name",)

    name = factory.Faker("country")
    code = factory.LazyAttribute(lambda obj: obj.name[:2].upper())


class ProvinceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Province
        django_get_or_create = ("name", "country")

    name = factory.Faker("state")
    country = factory.SubFactory(CountryFactory)


class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = City
        django_get_or_create = ("name", "province")

    name = factory.Faker("city")
    province = factory.SubFactory(ProvinceFactory)


class DistrictFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = District
        django_get_or_create = ("name", "city")

    name = factory.Faker("city_suffix")
    city = factory.SubFactory(CityFactory)
