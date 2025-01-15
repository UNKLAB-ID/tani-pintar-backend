from django.urls import path

from . import views
from .views import PostDetailView
from .views import PostListView

urlpatterns = [
    path("posts/", PostListView.as_view(), name="post-list"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="post-detail"),
    path("", views.index, name="index"),
]

app_name = "social_media"
