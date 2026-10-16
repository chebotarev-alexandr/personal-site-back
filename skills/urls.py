"""URL routes for skills."""

from django.urls import path

from .serializers import SkillGroupListView

app_name = "skills"

urlpatterns = [
    path("skills/", SkillGroupListView.as_view(), name="skill-list"),
]
