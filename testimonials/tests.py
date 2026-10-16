"""Smoke tests for the remaining public list endpoints."""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


class PublicListEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_empty_lists_return_200(self):
        endpoints = [
            "testimonials:testimonial-list",
            "skills:skill-list",
            "faq:faq-list",
            "blog:post-list",
            "services:category-list",
            "services:technology-list",
            "services:pricing-list",
            "services:process-list",
        ]
        for name in endpoints:
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, 200, name)
