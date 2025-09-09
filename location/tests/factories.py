import factory

from location.models import City
from location.models import Country
from location.models import District
from location.models import Province


class CountryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ("code",)

    name = "Indonesia"
    code = "ID"


class ProvinceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Province
        django_get_or_create = ("name", "country")

    country = factory.SubFactory(CountryFactory)
    name = factory.Sequence(lambda n: f"Province_{n}")  # Guaranteed unique names


class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = City
        django_get_or_create = ("name", "province")

    @factory.lazy_attribute
    def province(self):
        # This will be overridden when province is passed as parameter
        return ProvinceFactory()

    name = factory.Sequence(lambda n: f"City_{n}")  # Guaranteed unique names


class DistrictFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = District
        django_get_or_create = ("name", "city")

    @factory.lazy_attribute
    def city(self):
        # This will be overridden when city is passed as parameter
        return CityFactory()

    name = factory.Sequence(lambda n: f"District_{n}")  # Guaranteed unique names
