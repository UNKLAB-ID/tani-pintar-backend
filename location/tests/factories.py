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

    @factory.lazy_attribute
    def name(self):
        indonesia = Country.objects.get_or_create(
            code="ID",
            defaults={"name": "Indonesia"},
        )[0]
        provinces = Province.objects.filter(country=indonesia)
        if provinces.exists():
            return factory.random.randgen.choice(provinces).name
        return "Jawa Barat"  # fallback

    country = factory.SubFactory(CountryFactory)


class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = City
        django_get_or_create = ("name", "province")

    @factory.lazy_attribute
    def name(self):
        cities = City.objects.all()
        if cities.exists():
            return factory.random.randgen.choice(cities).name
        return "Jakarta Utara"  # fallback

    @factory.lazy_attribute
    def province(self):
        cities = City.objects.all()
        if cities.exists():
            return factory.random.randgen.choice(cities).province
        return ProvinceFactory()


class DistrictFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = District
        django_get_or_create = ("name", "city")

    @factory.lazy_attribute
    def name(self):
        districts = District.objects.all()
        if districts.exists():
            return factory.random.randgen.choice(districts).name
        return "Kemayoran"  # fallback

    @factory.lazy_attribute
    def city(self):
        districts = District.objects.all()
        if districts.exists():
            return factory.random.randgen.choice(districts).city
        return CityFactory()
