"""Проверка токена Яндекс SmartCaptcha."""

import json
import urllib.parse
import urllib.request

from django.conf import settings

VALIDATE_URL = "https://smartcaptcha.yandexcloud.net/validate"


def verify_smartcaptcha(token: str, ip: str) -> bool:
    """Валидирует токен Яндекс SmartCaptcha на сервере. True = прошёл капчу.

    Если серверный ключ не настроен — возвращает True (капча отключена).
    """
    secret = getattr(settings, "YC_SMARTCAPTCHA_SERVER_KEY", "")
    if not secret:
        return True  # капча не настроена — не блокируем формы
    if not token:
        return False

    params = urllib.parse.urlencode({"secret": secret, "token": token, "ip": ip})
    try:
        with urllib.request.urlopen(f"{VALIDATE_URL}?{params}", timeout=5) as resp:
            data = json.loads(resp.read())
            return data.get("status") == "ok"
    except Exception:  # noqa: BLE001 — сбой капчи не должен ронять форму
        return False
