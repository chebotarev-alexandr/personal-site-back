"""Проверка токена Яндекс SmartCaptcha."""

import json
import urllib.parse
import urllib.request

from django.conf import settings

VALIDATE_URL = "https://smartcaptcha.cloud.yandex.ru/validate"


def verify_smartcaptcha(token: str, ip: str) -> bool:
    """Возвращает True, если токен валиден.

    При сетевой ошибке/не-200 ответе возвращаем True (fail-open) — по
    рекомендации Яндекса, чтобы не блокировать пользователей из-за сбоя сервиса.
    """
    secret = getattr(settings, "YC_SMARTCAPTCHA_SERVER_KEY", "")
    if not secret:
        return True  # капча не настроена — не блокируем
    if not token:
        return False

    body = urllib.parse.urlencode({"secret": secret, "token": token, "ip": ip}).encode()
    request = urllib.request.Request(
        VALIDATE_URL,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return True  # сетевой сбой — пропускаем (fail-open)

    return payload.get("status") == "ok"
