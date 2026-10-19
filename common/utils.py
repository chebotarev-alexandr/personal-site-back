"""Small request helpers shared across the project."""


def get_client_ip(request) -> str:
    """Возвращает IP клиента с учётом прокси (X-Forwarded-For)."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")
