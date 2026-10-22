"""Tests for the chat API."""

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from chat.models import ChatMessage, ChatSession


@override_settings(CHAT_SECRET="test-secret", CHAT_BRIDGE_URL="")
class ChatApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_send_creates_session_and_message(self):
        resp = self.client.post(reverse("chat:chat-message-create"), {"text": "Привет"}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertIn("uid", resp.data)
        uid = resp.data["uid"]
        self.assertEqual(ChatSession.objects.count(), 1)
        self.assertEqual(ChatMessage.objects.count(), 1)
        self.assertEqual(ChatMessage.objects.first().direction, ChatMessage.Direction.INCOMING)

    def test_send_continues_existing_session(self):
        r1 = self.client.post(reverse("chat:chat-message-create"), {"text": "первое"}, format="json")
        uid = r1.data["uid"]
        r2 = self.client.post(reverse("chat:chat-message-create"), {"uid": uid, "text": "второе"}, format="json")
        self.assertEqual(r2.status_code, 201)
        self.assertEqual(r2.data["uid"], uid)
        self.assertEqual(ChatSession.objects.count(), 1)
        self.assertEqual(ChatMessage.objects.count(), 2)

    def test_empty_text_rejected(self):
        resp = self.client.post(reverse("chat:chat-message-create"), {"text": "  "}, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_poll_messages(self):
        r = self.client.post(reverse("chat:chat-message-create"), {"text": "hello"}, format="json")
        uid = r.data["uid"]
        resp = self.client.get(reverse("chat:chat-messages", kwargs={"uid": uid}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data["messages"]), 1)
        # no-store so nginx doesn't cache the poll response
        self.assertIn("no-store", resp["Cache-Control"])

    def test_reply_requires_secret(self):
        r = self.client.post(reverse("chat:chat-message-create"), {"text": "hello"}, format="json")
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
