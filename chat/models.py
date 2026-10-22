"""Chat sessions and messages for the on-site visitor chat widget."""

import uuid

from django.db import models

from common.models import TimeStampedModel


class ChatSession(TimeStampedModel):
    """One visitor chat. Keyed by an unguessable public UUID."""

    uid = models.UUIDField("Публичный ID", unique=True, default=uuid.uuid4, editable=False, db_index=True)
    ip = models.GenericIPAddressField("IP-адрес", null=True, blank=True)
    is_open = models.BooleanField("Открыт", default=True, db_index=True)

    class Meta:
        verbose_name = "Чат-сессия"
        verbose_name_plural = "Чат-сессии"
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.uid.hex[:8]} — {self.created_at:%d.%m %H:%M}"


class ChatMessage(TimeStampedModel):
    class Direction(models.TextChoices):
        INCOMING = "incoming", "От пользователя"
        OUTGOING = "outgoing", "От владельца"

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages", verbose_name="Сессия"
    )
    direction = models.CharField("Направление", max_length=10, choices=Direction.choices, db_index=True)
    text = models.TextField("Текст")

    class Meta:
        verbose_name = "Сообщение чата"
        verbose_name_plural = "Сообщения чата"
        ordering = ["created_at", "id"]

    def __str__(self) -> str:
        return f"{self.get_direction_display()}: {self.text[:40]}"
