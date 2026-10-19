"""Lead capture: every request/application form on the site.

A single ``Lead`` model stores every kind of lead (contact, callback,
order, brief, consultation, subscription). Form-specific required fields are
enforced at the serializer level; ``type`` is set by the view, never trusted
from the client.
"""

from django.db import models

from common.models import SortableModel, TimeStampedModel


class BudgetRange(SortableModel):
    """An editable budget option for the project-brief form."""

    label = models.CharField("Диапазон", max_length=120)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Диапазон бюджета"
        verbose_name_plural = "Диапазоны бюджета"

    def __str__(self) -> str:
        return self.label


class Lead(TimeStampedModel):
    """A single incoming lead."""

    class Type(models.TextChoices):
        CONTACT = "contact", "Обратная связь"
        CALLBACK = "callback", "Заказать звонок"
        ORDER_SERVICE = "order_service", "Заказ услуги"
        PROJECT_BRIEF = "project_brief", "Заявка на разработку"
        CONSULTATION = "consultation", "Консультация"
        SUBSCRIPTION = "subscription", "Подписка на рассылку"

    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        COMPLETED = "completed", "Завершена"
        REJECTED = "rejected", "Отклонена"
        SPAM = "spam", "Спам"

    type = models.CharField("Тип", max_length=20, choices=Type.choices, db_index=True)
    name = models.CharField("Имя", max_length=120, blank=True)
    email = models.EmailField("Email", blank=True)
    phone = models.CharField("Телефон", max_length=32, blank=True)
    company = models.CharField("Компания", max_length=160, blank=True)

    service = models.ForeignKey(
        "services.Service",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requests",
        verbose_name="Услуга",
    )
    budget = models.ForeignKey(
        BudgetRange,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requests",
        verbose_name="Бюджет",
    )
    deadline = models.CharField("Срок", max_length=120, blank=True)
    message = models.TextField("Сообщение", blank=True)

    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW, db_index=True)
    is_processed = models.BooleanField("Обработана", default=False, db_index=True)
    admin_note = models.TextField("Заметка менеджера", blank=True)

    ip = models.GenericIPAddressField("IP-адрес", null=True, blank=True)
    source = models.CharField("Источник (страница)", max_length=500, blank=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_type_display()} — {self.name or self.email or self.phone or self.pk}"


class BlockedIP(TimeStampedModel):
    """IP в чёрном списке (защита от DoS). Проверяется middleware + nginx."""

    ip = models.GenericIPAddressField("IP-адрес", unique=True)
    reason = models.CharField("Причина", max_length=255, blank=True)
    is_active = models.BooleanField("Активна", default=True, db_index=True)

    class Meta:
        verbose_name = "Заблокированный IP"
        verbose_name_plural = "Заблокированные IP"

    def __str__(self) -> str:
        return f"{self.ip} — {self.reason or 'без причины'}"


class LeadAttempt(TimeStampedModel):
    """Запись о каждой попытке отправки формы (для защиты от DoS)."""

    ip = models.GenericIPAddressField("IP-адрес", db_index=True)

    class Meta:
        verbose_name = "Попытка отправки формы"
        verbose_name_plural = "Попытки отправки форм"

    def __str__(self) -> str:
        return f"{self.ip} — {self.created_at:%d.%m.%Y %H:%M}"
