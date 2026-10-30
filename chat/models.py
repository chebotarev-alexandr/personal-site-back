"""Chat sessions and messages for the on-site visitor chat widget."""

import uuid

from django.db import models

from common.models import TimeStampedModel


class ChatSession(TimeStampedModel):
    """One visitor chat. Keyed by an unguessable public UUID."""

    uid = models.UUIDField("Публичный ID", unique=True, default=uuid.uuid4, editable=False, db_index=True)
    ip = models.GenericIPAddressField("IP-адрес", null=True, blank=True)
    name = models.CharField("Имя посетителя", max_length=120, blank=True, default="")
    contact = models.CharField("Контакт для связи", max_length=255, blank=True, default="")
    # Когда посетитель последний раз успешно прошёл капчу (антиспам-«льгота»).
    captcha_passed_at = models.DateTimeField("Капча пройдена", null=True, blank=True)
    is_open = models.BooleanField("Открыт", default=True, db_index=True)

    class Meta:
        verbose_name = "Чат-сессия"
        verbose_name_plural = "Чат-сессии"
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        label = self.name or self.uid.hex[:8]
        return f"{label} — {self.created_at:%d.%m %H:%M}"


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


class ChatAttempt(TimeStampedModel):
    """Запись о каждой попытке отправить сообщение (для защиты от спама)."""

    ip = models.GenericIPAddressField("IP-адрес", db_index=True)

    class Meta:
        verbose_name = "Попытка сообщения в чате"
        verbose_name_plural = "Попытки сообщений в чате"

    def __str__(self) -> str:
        return f"{self.ip} — {self.created_at:%d.%m.%Y %H:%M}"
