"""URL routes for blog."""

from django.urls import path

from .serializers import PostViewSet

app_name = "blog"

urlpatterns = [
    path("blog/", PostViewSet.as_view({"get": "list"}), name="post-list"),
    path("blog/<slug:slug>/", PostViewSet.as_view({"get": "retrieve"}), name="post-detail"),
]
