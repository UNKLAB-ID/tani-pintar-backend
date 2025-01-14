from django.urls import path

from . import views

urlpatterns = [path("", views.index)]

app_name = "social_media"
