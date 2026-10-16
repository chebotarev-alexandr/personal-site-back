"""Validators shared across apps."""

import re

from django.core.exceptions import ValidationError

PHONE_DIGITS = re.compile(r"\D")


def validate_phone(value: str) -> None:
    """Accept common phone formats; require 10–15 digits."""
    digits = PHONE_DIGITS.sub("", value or "")
    if not 10 <= len(digits) <= 15:
        raise ValidationError("Введите корректный номер телефона.")
