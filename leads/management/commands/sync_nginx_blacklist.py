"""Синхронизирует чёрный список IP в файл для nginx (deny <ip>;)."""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from leads.models import BlockedIP


class Command(BaseCommand):
    help = "Пишет заблокированные IP в файл для nginx. Выводит changed/unchanged."

    def handle(self, *args, **options):
        path = Path(settings.NGINX_BLACKLIST_FILE)
        lines = []
        for entry in BlockedIP.objects.filter(is_active=True).order_by("ip"):
            reason = f" # {entry.reason}" if entry.reason else ""
            lines.append(f"deny {entry.ip};{reason}\n")

        content = "".join(lines)
        path.parent.mkdir(parents=True, exist_ok=True)

        changed = not path.exists() or path.read_text() != content
        if changed:
            path.write_text(content)
        self.stdout.write("changed" if changed else "unchanged")
