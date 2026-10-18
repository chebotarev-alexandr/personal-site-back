"""Notification helpers for new leads: email + Telegram."""

import json
import logging
import threading
import urllib.request

from django.conf import settings
from django.core.mail import send_mail

from .models import Lead

logger = logging.getLogger(__name__)


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


def _telegram_config():
    """Resolve Telegram settings: admin (SiteSettings) overrides env vars."""
    from core.models import SiteSettings

    token = ""
    chat_id = ""
    enabled = True
    try:
        site = SiteSettings.load()
        token = site.telegram_bot_token or ""
        chat_id = site.telegram_chat_id or ""
        enabled = site.telegram_alerts_enabled
    except Exception:  # pragma: no cover — DB may be unavailable during migrations
        logger.debug("SiteSettings unavailable for Telegram config", exc_info=True)

    token = token or settings.TELEGRAM_BOT_TOKEN
    chat_id = chat_id or settings.TELEGRAM_CHAT_ID
    return enabled, token, chat_id


def _send_telegram(token: str, chat_id: str, text: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            return response.status == 200
    except Exception as exc:  # noqa: BLE001 - fail-silent by design
        logger.warning("Telegram notify failed: %s", exc)
        return False


def notify_lead(lead: Lead) -> None:
    """Notify about a new lead: email (if configured) + Telegram (if configured)."""
    recipient = settings.LEAD_NOTIFY_EMAIL
    if recipient:
        send_mail(
            subject=f"Новая заявка: {lead.get_type_display()}",
            message=_lead_summary(lead),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=True,
        )

    enabled, token, chat_id = _telegram_config()
    if not (enabled and token and chat_id):
        return

    text = f"🔔 Новая заявка с сайта\n\n{_lead_summary(lead)}"
    # Off the request path so form submission stays fast.
    threading.Thread(
        target=_send_telegram, args=(token, chat_id, text), daemon=True
    ).start()
