"""Tests for the aggregated site endpoint."""

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import HeroSection, SiteSettings, SocialLink, Stat


class SiteViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        SiteSettings.load()
        HeroSection.load()
        SocialLink.objects.create(platform=SocialLink.Platform.GITHUB, url="https://github.com/x")
        Stat.objects.create(value="5+", label="лет")

    def test_site_returns_all_blocks(self):
        resp = self.client.get(reverse("core:site"))
        self.assertEqual(resp.status_code, 200)
        for key in ("settings", "hero", "about", "stats", "socials"):
            self.assertIn(key, resp.data)
        self.assertEqual(resp.data["socials"][0]["platform"], SocialLink.Platform.GITHUB)
