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
    path("refresh-token/", views.RefreshTokenView.as_view(), name="refresh-token"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("login/confirm", views.ConfirmLoginView.as_view(), name="confirm-login"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "profile/<int:profile_id>/",
        views.ProfileDetailAPIView.as_view(),
        name="profile-detail-by-id",
    ),
]

app_name = "accounts"
