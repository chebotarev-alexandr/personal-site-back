"""Views for the projects app."""

from rest_framework import viewsets

from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectSerializer
    lookup_field = "slug"
    filterset_fields = ["tags__slug", "is_featured"]
    search_fields = ["title", "short_description", "description"]
    ordering_fields = ["sort_order", "year", "title"]
    ordering = ["sort_order"]

    def get_queryset(self):
        return Project.objects.filter(is_active=True).prefetch_related("tags", "images")
