from django.test import TestCase

from location.models import City
from location.models import Country
from location.models import Province


class CountryModelTest(TestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        self.country = Country.objects.create(name="Test Country", code="TC")

    def test_country_creation(self):
        country = Country.objects.get(code="TC")
        assert country.name == "Test Country"
        assert country.code == "TC"

    def test_country_str(self):
        assert str(self.country.name) == "Test Country"


class ProvinceModelTest(TestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        self.country = Country.objects.create(name="Test Country", code="TC")
        self.province = Province.objects.create(
            name="Test Province",
            country=self.country,
        )

    def test_province_creation(self):
        province = Province.objects.get(id=self.province.id)
        assert province.name == "Test Province"
        assert province.country == self.country

    def test_province_str(self):
        assert str(self.province.name) == "Test Province"


class CityModelTest(TestCase):
    fixtures = ["initial_data.json"]

    def setUp(self):
        self.country = Country.objects.create(name="Test Country", code="TC")
        self.province = Province.objects.create(
            name="Test Province",
            country=self.country,
        )
        self.city = City.objects.create(name="Test City", province=self.province)

    def test_city_creation(self):
        city = City.objects.get(id=self.city.id)
        assert city.name == "Test City"
        assert city.province == self.province

    def test_city_str(self):
        assert str(self.city.name) == "Test City"
