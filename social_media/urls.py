from django.urls import path

from . import views
from .views import PostListView

urlpatterns = [
    path("posts/", PostListView.as_view()),
    path("", views.index),
]

app_name = "social_media"
