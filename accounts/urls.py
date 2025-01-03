from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "register/confirm",
        views.ConfirmRegistrationView.as_view(),
        name="confirm-registration",
    ),
]

app_name = "accounts"
