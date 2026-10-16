"""Email notification helper for new leads."""

from django.conf import settings
from django.core.mail import send_mail

from .models import Lead


def _lead_summary(lead: Lead) -> str:
    lines = [
        f"Тип: {lead.get_type_display()}",
        f"Имя: {lead.name or '—'}",
        f"Email: {lead.email or '—'}",
        f"Телефон: {lead.phone or '—'}",
        f"Компания: {lead.company or '—'}",
        f"Услуга: {lead.service.title if lead.service else '—'}",
        f"Бюджет: {lead.budget.label if lead.budget else '—'}",
        f"Срок: {lead.deadline or '—'}",
        f"Сообщение:\n{lead.message or '—'}",
    ]
    return "\n".join(lines)


def notify_lead(lead: Lead) -> None:
    """Send a notification email about a new lead, if configured."""
    recipient = settings.LEAD_NOTIFY_EMAIL
    if not recipient:
        return
    send_mail(
        subject=f"Новая заявка: {lead.get_type_display()}",
        message=_lead_summary(lead),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=True,
    )
