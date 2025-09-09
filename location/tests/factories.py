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

    @factory.lazy_attribute
    def name(self):
        provinces = Province.objects.filter(country=self.country)
        if provinces.exists():
            return factory.random.randgen.choice(provinces).name
        return f"{self.country.name} Province"  # deterministic fallback


class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = City
        django_get_or_create = ("name", "province")

    province = factory.SubFactory(ProvinceFactory)

    @factory.lazy_attribute
    def name(self):
        cities = City.objects.filter(province=self.province)
        if cities.exists():
            return factory.random.randgen.choice(cities).name
        return f"{self.province.name} City"  # fallback that matches province


class DistrictFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = District
        django_get_or_create = ("name", "city")

    city = factory.SubFactory(CityFactory)

    @factory.lazy_attribute
    def name(self):
        districts = District.objects.filter(city=self.city)
        if districts.exists():
            return factory.random.randgen.choice(districts).name
        return f"{self.city.name} District"  # fallback that matches city
