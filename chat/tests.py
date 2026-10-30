"""Tests for the chat API."""

from datetime import timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from chat.models import ChatAttempt, ChatMessage, ChatSession
from leads.models import BlockedIP

CHAT_URL = "chat:chat-message-create"


@override_settings(CHAT_SECRET="test-secret", CHAT_BRIDGE_URL="")
class ChatApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_send_creates_session_and_message(self):
        resp = self.client.post(reverse(CHAT_URL), {"text": "Привет", "name": "Саша"}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertIn("uid", resp.data)
        uid = resp.data["uid"]
        self.assertEqual(ChatSession.objects.count(), 1)
        self.assertEqual(ChatMessage.objects.count(), 1)
        self.assertEqual(ChatMessage.objects.first().direction, ChatMessage.Direction.INCOMING)
        self.assertEqual(ChatSession.objects.first().uid.hex, uid.replace("-", ""))

    def test_first_message_requires_name(self):
        resp = self.client.post(reverse(CHAT_URL), {"text": "Привет"}, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_name_and_contact_stored(self):
        resp = self.client.post(
            reverse(CHAT_URL), {"text": "Привет", "name": "Саша", "contact": "@telegram"}, format="json"
        )
        self.assertEqual(resp.status_code, 201)
        session = ChatSession.objects.first()
        self.assertEqual(session.name, "Саша")
        self.assertEqual(session.contact, "@telegram")

    def test_contact_optional(self):
        resp = self.client.post(reverse(CHAT_URL), {"text": "Привет", "name": "Саша"}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(ChatSession.objects.first().contact, "")

    def test_send_continues_existing_session(self):
        r1 = self.client.post(reverse(CHAT_URL), {"text": "первое", "name": "Саша"}, format="json")
        uid = r1.data["uid"]
        r2 = self.client.post(
            reverse(CHAT_URL), {"uid": uid, "text": "второе", "name": "Саша"}, format="json"
        )
        self.assertEqual(r2.status_code, 201)
        self.assertEqual(r2.data["uid"], uid)
        self.assertEqual(ChatSession.objects.count(), 1)
        self.assertEqual(ChatMessage.objects.count(), 2)

    def test_empty_text_rejected(self):
        resp = self.client.post(reverse(CHAT_URL), {"text": "  ", "name": "Саша"}, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_poll_messages(self):
        r = self.client.post(reverse(CHAT_URL), {"text": "hello", "name": "Саша"}, format="json")
        uid = r.data["uid"]
        resp = self.client.get(reverse("chat:chat-messages", kwargs={"uid": uid}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["messages"]), 1)
        # no-store so nginx doesn't cache the poll response
        self.assertIn("no-store", resp["Cache-Control"])

    def test_reply_requires_secret(self):
        r = self.client.post(reverse(CHAT_URL), {"text": "hello", "name": "Саша"}, format="json")
        uid = r.data["uid"]

        bad = self.client.post(reverse("chat:chat-reply", kwargs={"uid": uid}), {"text": "no"}, format="json")
        self.assertEqual(bad.status_code, 403)

        good = self.client.post(
            reverse("chat:chat-reply", kwargs={"uid": uid}),
            {"text": "ответ"},
            format="json",
            HTTP_X_CHAT_SECRET="test-secret",
        )
        self.assertEqual(good.status_code, 201)
        self.assertEqual(ChatMessage.objects.filter(direction=ChatMessage.Direction.OUTGOING).count(), 1)

    def test_reply_unknown_session_404(self):
        resp = self.client.post(
            reverse("chat:chat-reply", kwargs={"uid": "00000000-0000-0000-0000-000000000000"}),
            {"text": "x"},
            format="json",
            HTTP_X_CHAT_SECRET="test-secret",
        )
        self.assertEqual(resp.status_code, 404)


@override_settings(
    CHAT_SECRET="test-secret",
    CHAT_BRIDGE_URL="",
    CHAT_SPAM_MAX_MESSAGES=2,
    CHAT_SPAM_WINDOW_SECONDS=60,
    CHAT_BLACKLIST_THRESHOLD=100,
    YC_SMARTCAPTCHA_SERVER_KEY="test-key",
)
class ChatCaptchaTests(TestCase):
    """Rate-limit за короткое окно → требование капчи."""

    def setUp(self):
        self.client = APIClient()

    def test_rate_limit_requires_captcha(self):
        url = reverse(CHAT_URL)
        uid = None
        for i in range(2):
            payload = {"text": f"сообщение {i}", "name": "Саша"}
            if uid:
                payload["uid"] = uid
            r = self.client.post(url, payload, format="json")
            self.assertEqual(r.status_code, 201, msg=r.data)
            uid = r.data["uid"]

        # 3-е сообщение за окно → капча (токена нет) → 400 captcha_required
        r = self.client.post(url, {"uid": uid, "text": "третье", "name": "Саша"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(r.data["code"], "captcha_required")
        # сообщение НЕ создано
        self.assertEqual(ChatMessage.objects.count(), 2)

    def test_captcha_grace_period_skips_verification(self):
        url = reverse(CHAT_URL)
        uid = None
        for i in range(2):
            payload = {"text": f"сообщение {i}", "name": "Саша"}
            if uid:
                payload["uid"] = uid
            r = self.client.post(url, payload, format="json")
            uid = r.data["uid"]

        # помечаем, что капча только что пройдена
        ChatSession.objects.update(captcha_passed_at=timezone.now())

        r = self.client.post(url, {"uid": uid, "text": "третье", "name": "Саша"}, format="json")
        self.assertEqual(r.status_code, 201)


@override_settings(
    CHAT_SECRET="test-secret",
    CHAT_BRIDGE_URL="",
    CHAT_SPAM_MAX_MESSAGES=100,
    CHAT_BLACKLIST_THRESHOLD=3,
    YC_SMARTCAPTCHA_SERVER_KEY="",
)
class ChatBlockTests(TestCase):
    """Много попыток за час → блокировка IP."""

    def setUp(self):
        self.client = APIClient()

    def test_block_after_many_attempts(self):
        url = reverse(CHAT_URL)
        for i in range(2):
            r = self.client.post(url, {"text": f"м{i}", "name": "Саша"}, format="json")
            self.assertEqual(r.status_code, 201, msg=r.data)

        # 3-я попытка → порог блокировки достигнут → 403 + IP в чёрном списке
        r = self.client.post(url, {"text": "м3", "name": "Саша"}, format="json")
        self.assertEqual(r.status_code, 403)
        self.assertTrue(BlockedIP.objects.filter(ip="127.0.0.1", is_active=True).exists())

    def test_blocked_ip_stays_blocked(self):
        BlockedIP.objects.create(ip="127.0.0.1", reason="тест")
        r = self.client.post(reverse(CHAT_URL), {"text": "х", "name": "Саша"}, format="json")
        self.assertEqual(r.status_code, 403)

    def test_attempts_recorded_even_on_rejection(self):
        url = reverse(CHAT_URL)
        # пустое сообщение → 400, но попытка зафиксирована
        self.client.post(url, {"text": "  ", "name": "Саша"}, format="json")
        self.assertEqual(ChatAttempt.objects.count(), 1)
