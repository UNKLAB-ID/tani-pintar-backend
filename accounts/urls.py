from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("register/", views.RegisterView.as_view(), name="register"),
]

app_name = "accounts"
