"""Вручную блокирует/разблокирует IP в чёрном списке.

Usage::

    python manage.py block_ip 1.2.3.4 --reason "DoS"
    python manage.py block_ip 1.2.3.4 --unblock
"""

from django.core.management.base import BaseCommand

from leads.models import BlockedIP


class Command(BaseCommand):
    help = "Блокирует/разблокирует IP в чёрном списке."

    def add_arguments(self, parser):
        parser.add_argument("ip")
        parser.add_argument("--reason", default="Заблокирован вручную")
        parser.add_argument("--unblock", action="store_true")

    def handle(self, *args, **options):
        ip = options["ip"]
        if options["unblock"]:
            BlockedIP.objects.filter(ip=ip).update(is_active=False)
            self.stdout.write(self.style.SUCCESS(f"IP {ip} разблокирован."))
        else:
            BlockedIP.objects.update_or_create(
                ip=ip, defaults={"reason": options["reason"], "is_active": True}
            )
            self.stdout.write(self.style.SUCCESS(f"IP {ip} заблокирован."))
