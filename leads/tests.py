"""Tests for lead endpoints — every form type and its validation."""

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from leads.models import BlockedIP, BudgetRange, Lead
from services.models import Service, ServiceCategory


class LeadEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        category = ServiceCategory.objects.create(name="Веб", slug="web")
        self.service = Service.objects.create(title="Лендинг", slug="landing", category=category, is_active=True)
        self.budget = BudgetRange.objects.create(label="до 50 000 ₽")

    def _post(self, name, payload):
        return self.client.post(reverse(f"leads:{name}"), payload, format="json")

    def test_contact_creates_lead(self):
        resp = self._post(
            "contact",
            {"name": "Иван", "email": "ivan@example.com", "phone": "+7 900 000-00-00", "message": "Привет"},
        )
        self.assertEqual(resp.status_code, 201)
        lead = Lead.objects.get()
        self.assertEqual(lead.type, Lead.Type.CONTACT)
        self.assertEqual(lead.name, "Иван")

    def test_callback_requires_phone(self):
        resp = self._post("callback", {"name": "Иван"})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("phone", resp.data)

    def test_order_service_links_service_by_slug(self):
        resp = self._post(
            "order",
            {"name": "Иван", "phone": "+79000000000", "service": "landing"},
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Lead.objects.get().service, self.service)

    def test_order_service_rejects_unknown_slug(self):
        resp = self._post(
            "order",
            {"name": "Иван", "phone": "+79000000000", "service": "nope"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_brief_creates_lead_with_budget(self):
        resp = self._post(
            "brief",
            {
                "name": "Иван",
                "email": "ivan@example.com",
                "service": "landing",
                "budget": self.budget.pk,
                "deadline": "месяц",
                "message": "Нужен сайт",
            },
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Lead.objects.get().budget, self.budget)
        self.assertEqual(Lead.objects.get().type, Lead.Type.PROJECT_BRIEF)

    def test_consultation_creates_lead(self):
        resp = self._post("consultation", {"name": "Иван", "phone": "+79000000000"})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Lead.objects.get().type, Lead.Type.CONSULTATION)

    def test_subscribe_requires_email_only(self):
        resp = self._post("subscribe", {"email": "ivan@example.com"})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Lead.objects.get().type, Lead.Type.SUBSCRIPTION)

    def test_invalid_phone_rejected(self):
        resp = self._post("callback", {"name": "Иван", "phone": "123"})
        self.assertEqual(resp.status_code, 400)

    def test_client_cannot_override_type(self):
        resp = self._post(
            "contact",
            {"name": "Иван", "email": "i@example.com", "type": Lead.Type.CALLBACK},
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Lead.objects.get().type, Lead.Type.CONTACT)

    def test_budget_list(self):
        resp = self.client.get(reverse("leads:budgets"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_lead_post_ignores_admin_session_csrf(self):
        """Form POSTs must stay 201 even when a browser session cookie exists."""
        from django.contrib.auth import get_user_model

        User = get_user_model()
        User.objects.create_user("manager", password="pw")
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(User.objects.get(username="manager"))

        resp = client.post(
            reverse("leads:contact"),
            {"name": "Иван", "email": "i@example.com"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)

    def test_rate_limit_blocks_after_limit(self):
        payload = {"name": "Иван", "email": "i@example.com"}
        for _ in range(3):
            self.assertEqual(self._post("contact", payload).status_code, 201)
        self.assertEqual(self._post("contact", payload).status_code, 429)

    def test_sql_injection_rejected(self):
        resp = self._post(
            "contact",
            {"name": "Иван", "email": "i@example.com", "message": "'; DROP TABLE leads; --"},
        )
        self.assertEqual(resp.status_code, 400)

    @override_settings(YC_SMARTCAPTCHA_SERVER_KEY="test-secret")
    def test_captcha_required_on_repeat(self):
        payload = {"name": "Иван", "email": "i@example.com"}
        self.assertEqual(self._post("contact", payload).status_code, 201)
        resp = self._post("contact", payload)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data.get("code"), "captcha_required")

    def test_blocked_ip_forbidden(self):
        BlockedIP.objects.create(ip="127.0.0.1")
        resp = self._post("contact", {"name": "Иван", "email": "i@example.com"})
        self.assertEqual(resp.status_code, 403)
