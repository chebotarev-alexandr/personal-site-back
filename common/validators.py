"""Validators shared across apps."""

import re

from django.core.exceptions import ValidationError

PHONE_DIGITS = re.compile(r"\D")

# Признаки SQL-инъекций. ORM и так использует параметризованные запросы,
# но это защита в глубину: отклоняем явные попытки инъекций в полях формы.
_SQLI_PATTERNS = [
    r"\bunion\s+(all\s+)?select\b",
    r"\bselect\b.{0,40}\bfrom\b",
    r"\bdrop\s+table\b",
    r"\binsert\s+into\b",
    r"\bupdate\b.{0,40}\bset\b",
    r"\bdelete\s+from\b",
    r"\bsleep\s*\(",
    r"\bbenchmark\s*\(",
    r"\binformation_schema\b",
    r"\bsp_executesql\b|\bexec\s*\(",
    r"\bwaitfor\s+delay\b",
]
_SQLI_RES = [re.compile(p, re.IGNORECASE) for p in _SQLI_PATTERNS]


def validate_phone(value: str) -> None:
    """Accept common phone formats; require 10–15 digits."""
    digits = PHONE_DIGITS.sub("", value or "")
    if not 10 <= len(digits) <= 15:
        raise ValidationError("Введите корректный номер телефона.")


def validate_no_sql_injection(value: str) -> None:
    """Отклоняет строки с признаками SQL-инъекций."""
    if not value:
        return
    for pattern in _SQLI_RES:
        if pattern.search(value):
            raise ValidationError("Поле содержит недопустимые символы.")
