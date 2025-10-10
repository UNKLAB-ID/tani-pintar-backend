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
    """Factory that returns a random existing Province from fixtures.

    Respects the Country relationship. If a country is provided,
    returns a province from that country.
    """

    class Meta:
        model = Province

    @classmethod
    def _create(cls, *_args, **kwargs):
        """Return random existing province instead of creating new one."""
        country = kwargs.get("country")

        if country:
            # Get a random province from the specified country
            return Province.objects.filter(country=country).order_by("?").first()
        # Get any random province
        return Province.objects.order_by("?").first()


class CityFactory(factory.django.DjangoModelFactory):
    """Factory that returns a random existing City from fixtures.

    Respects the Province relationship. If a province is provided,
    returns a city from that province. If a country is provided,
    returns a city from a province in that country.
    """

    class Meta:
        model = City

    @classmethod
    def _create(cls, *_args, **kwargs):
        """Return random existing city instead of creating new one."""
        province = kwargs.get("province")
        country = kwargs.get("country")

        if province:
            # Get a random city from the specified province
            return City.objects.filter(province=province).order_by("?").first()
        if country:
            # Get a random city from any province in the specified country
            return City.objects.filter(province__country=country).order_by("?").first()
        # Get any random city
        return City.objects.order_by("?").first()


class DistrictFactory(factory.django.DjangoModelFactory):
    """Factory that returns a random existing District from fixtures.

    Respects the City relationship. If a city is provided,
    returns a district from that city. If a province is provided,
    returns a district from a city in that province. If a country is provided,
    returns a district from a city in a province in that country.
    """

    class Meta:
        model = District

    @classmethod
    def _create(cls, *_args, **kwargs):
        """Return random existing district instead of creating new one."""
        city = kwargs.get("city")
        province = kwargs.get("province")
        country = kwargs.get("country")

        if city:
            # Get a random district from the specified city
            return District.objects.filter(city=city).order_by("?").first()
        if province:
            # Get a random district from any city in the specified province
            return (
                District.objects.filter(city__province=province).order_by("?").first()
            )
        if country:
            # Get a random district from a city in a province in the country
            return (
                District.objects.filter(city__province__country=country)
                .order_by("?")
                .first()
            )
        # Get any random district
        return District.objects.order_by("?").first()
