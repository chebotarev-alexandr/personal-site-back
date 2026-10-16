"""URL routes for the projects app."""

from django.urls import path

from .views import ProjectViewSet

app_name = "projects"

urlpatterns = [
    path("projects/", ProjectViewSet.as_view({"get": "list"}), name="project-list"),
    path("projects/<slug:slug>/", ProjectViewSet.as_view({"get": "retrieve"}), name="project-detail"),
]
