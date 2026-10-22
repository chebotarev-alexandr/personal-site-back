"""Chat notification: forward a new visitor message to the owner's Telegram.

The production VPS can't reach api.telegram.org directly (RU ISP block), so the
message is relayed through the chat bridge on the Amsterdam box (which also runs
the bot long-poll and routes the owner's replies back via the reply endpoint).
"""

import json
import logging
import threading
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)


def _send(payload: dict) -> bool:
    bridge_url = getattr(settings, "CHAT_BRIDGE_URL", "")
    if not bridge_url:
        return False
    req = urllib.request.Request(
        bridge_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status == 200
    except Exception as exc:  # noqa: BLE001 — fail-silent, chat is best-effort
        logger.warning("Chat bridge notify failed: %s", exc)
        return False


def notify_chat_message(session, message) -> None:
    """Notify the owner about a new incoming chat message (off the request path)."""
    secret = getattr(settings, "CHAT_SECRET", "")
    text = (
        "🔔 Новое сообщение в чате сайта\n\n"
        f"💬 {message.text}\n\n"
        f"🔑 Сессия: {session.uid.hex[:8]}"
    )
    payload = {"secret": secret, "session_uid": str(session.uid), "text": text}
    threading.Thread(target=_send, args=(payload,), daemon=True).start()
