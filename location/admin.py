from django.contrib import admin

from location.models import City
from location.models import Country
from location.models import District
from location.models import Province


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name",)
    list_filter = ("country",)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "province")
    search_fields = ("name",)
    list_filter = ("province",)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name", "city")
    search_fields = ("name",)
    list_filter = ("city",)
