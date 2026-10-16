"""Tests for services endpoints."""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from services.models import Service, ServiceCategory


class ServiceEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.web = ServiceCategory.objects.create(name="Веб", slug="web")
        self.bot = ServiceCategory.objects.create(name="Боты", slug="bots")
        Service.objects.create(title="Лендинг", slug="landing", category=self.web, is_featured=True)
        Service.objects.create(title="Бот", slug="bot", category=self.bot)

    def test_list_returns_active_services(self):
        resp = self.client.get(reverse("services:service-list"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 2)

    def test_filter_by_category(self):
        resp = self.client.get(reverse("services:service-list"), {"category__slug": "web"})
        self.assertEqual(resp.data["count"], 1)

    def test_filter_featured(self):
        resp = self.client.get(reverse("services:service-list"), {"is_featured": "true"})
        self.assertEqual(resp.data["count"], 1)

    def test_detail_by_slug(self):
        resp = self.client.get(reverse("services:service-detail", kwargs={"slug": "landing"}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["slug"], "landing")


class ReferenceListEndpointsTests(TestCase):
    """Categories/technologies/pricing/process must return plain arrays (frontend expects lists)."""

    def setUp(self):
        self.client = APIClient()

    def test_reference_endpoints_return_lists_not_paginated(self):
        endpoints = [
            "services:category-list",
            "services:technology-list",
            "services:pricing-list",
            "services:process-list",
        ]
        for name in endpoints:
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, 200, name)
            self.assertIsInstance(
                resp.data,
                list,
                f"{name} должен отдавать список, а не объект пагинации",
            )
