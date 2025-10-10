import factory

from location.models import City
from location.models import Country
from location.models import District
from location.models import Province


class CountryFactory(factory.django.DjangoModelFactory):
    """Factory that returns a random existing Country from fixtures."""

    class Meta:
        model = Country

    @classmethod
    def _create(cls, *_args, **_kwargs):
        """Return random existing country instead of creating new one."""
        return Country.objects.order_by("?").first()


class ProvinceFactory(factory.django.DjangoModelFactory):
    """Factory that returns a random existing Province from fixtures."""

    class Meta:
        model = Province

    @classmethod
    def _create(cls, *_args, **_kwargs):
        """Return random existing province instead of creating new one."""
        return Province.objects.order_by("?").first()


class CityFactory(factory.django.DjangoModelFactory):
    """Factory that returns a random existing City from fixtures."""

    class Meta:
        model = City

    @classmethod
    def _create(cls, *_args, **_kwargs):
        """Return random existing city instead of creating new one."""
        return City.objects.order_by("?").first()


class DistrictFactory(factory.django.DjangoModelFactory):
    """Factory that returns a random existing District from fixtures."""

    class Meta:
        model = District

    @classmethod
    def _create(cls, *_args, **_kwargs):
        """Return random existing district instead of creating new one."""
        return District.objects.order_by("?").first()
