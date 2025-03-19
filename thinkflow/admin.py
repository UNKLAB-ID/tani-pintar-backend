from django.contrib import admin

from .models import PlantDisease


@admin.register(PlantDisease)
class PlantDiseaseAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "user",
        "created_at",
    )
    search_fields = ("uuid", "user__name", "user__email")
    readonly_fields = ("uuid", "created_at")
