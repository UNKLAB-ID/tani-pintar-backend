from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from location.models import City
from location.models import Country
from location.models import District
from location.models import Province


class BaseLocationTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Test Country", code="TC")
        self.province = Province.objects.create(
            name="Test Province",
            country=self.country,
        )
        self.city = City.objects.create(name="Test City", province=self.province)
        self.district = District.objects.create(name="Test District", city=self.city)


class CountryViewTests(BaseLocationTest):
    def test_country_list_view(self):
        response = self.client.get(reverse("location:countries"))
        assert response.status_code == status.HTTP_200_OK
        self.assertContains(response, "Test Country")

    def test_country_detail_view(self):
        response = self.client.get(
            reverse("location:country-detail", kwargs={"pk": self.country.pk}),
        )
        assert response.status_code == status.HTTP_200_OK


class ProvinceViewTests(BaseLocationTest):
    def test_province_list_view(self):
        response = self.client.get(reverse("location:provinces"))
        assert response.status_code == status.HTTP_200_OK
        self.assertContains(response, "Test Province")

    def test_province_detail_view(self):
        response = self.client.get(
            reverse("location:province-detail", kwargs={"pk": self.province.pk}),
        )
        assert response.status_code == status.HTTP_200_OK


class CityViewTests(BaseLocationTest):
    def test_city_list_view(self):
        response = self.client.get(reverse("location:cities"))
        assert response.status_code == status.HTTP_200_OK
        self.assertContains(response, "Test City")

    def test_city_detail_view(self):
        response = self.client.get(
            reverse("location:city-detail", kwargs={"pk": self.city.pk}),
        )
        assert response.status_code == status.HTTP_200_OK
