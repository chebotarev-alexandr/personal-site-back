"""Middleware для базовой защиты от DoS: блокировка по чёрному списку IP."""

from django.http import HttpResponseForbidden

from common.utils import get_client_ip


class BlockedIPMiddleware:
    """Отдаёт 403 для IP из чёрного списка (проверяется до обработки запроса)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = get_client_ip(request)
        if ip and self._is_blocked(ip):
            return HttpResponseForbidden("Доступ с вашего IP ограничен.")
        return self.get_response(request)

    @staticmethod
    def _is_blocked(ip: str) -> bool:
        # Ленивый импорт — модель не готова на этапе загрузки middleware.
        from leads.models import BlockedIP

        return BlockedIP.objects.filter(ip=ip, is_active=True).exists()
