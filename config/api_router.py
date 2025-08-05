from django.conf import settings
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from core.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)

# Additional URL patterns for non-ViewSet based views
additional_patterns = [
    path("ecommerce/", include("ecommerce.urls", namespace="ecommerce")),
]

app_name = "api"
urlpatterns = router.urls + additional_patterns
