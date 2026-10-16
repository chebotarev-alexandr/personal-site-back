"""Tests for projects endpoints."""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from projects.models import Project, ProjectTag


class ProjectEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        tag = ProjectTag.objects.create(name="Django", slug="django")
        project = Project.objects.create(title="Телеметрия", slug="telemetry", short_description="x", is_featured=True)
        project.tags.add(tag)

    def test_list(self):
        resp = self.client.get(reverse("projects:project-list"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)

    def test_filter_by_tag(self):
        resp = self.client.get(reverse("projects:project-list"), {"tags__slug": "django"})
        self.assertEqual(resp.data["count"], 1)

    def test_detail(self):
        resp = self.client.get(reverse("projects:project-detail", kwargs={"slug": "telemetry"}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["slug"], "telemetry")
