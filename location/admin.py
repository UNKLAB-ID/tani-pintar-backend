from django.contrib import admin
from django.db.models import Q
from unfold.admin import ModelAdmin

from location.models import City
from location.models import Country
from location.models import District
from location.models import Province


@admin.register(Country)
class CountryAdmin(ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(Province)
class ProvinceAdmin(ModelAdmin):
    list_display = ("name", "country")
    search_fields = ("name",)
    list_filter = ("country",)


@admin.register(City)
class CityAdmin(ModelAdmin):
    list_display = ("name", "province")
    search_fields = ("name",)
    list_filter = ("province",)

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            query = Q()
            for field in self.search_fields:
                query |= Q(**{f"{field}__icontains": search_term})
            queryset = queryset.filter(query)
        return queryset, False


@admin.register(District)
class DistrictAdmin(ModelAdmin):
    list_display = ("name", "city")
    search_fields = ("name",)
    list_filter = ("city",)
