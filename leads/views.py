"""Views for lead capture and budget options.

Формы защищены: чёрный список IP, rate-limit (N заявок в сутки) и
Яндекс SmartCaptcha на повторную отправку с одного IP.
"""

from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from common.utils import get_client_ip

from .captcha import verify_smartcaptcha
from .models import BlockedIP, BudgetRange, Lead, LeadAttempt
from .notify import notify_lead
from .serializers import (
    BriefSerializer,
    BudgetRangeSerializer,
    CallbackSerializer,
    ConsultationSerializer,
    ContactSerializer,
    OrderServiceSerializer,
    SubscribeSerializer,
)


class LeadCreateView(generics.CreateAPIView):
    """Base for all lead endpoints: защита + фиксация ip/source + уведомления."""

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        ip = get_client_ip(request)

        # Фиксируем каждую попытку — по ним считаем DoS-порог чёрного списка.
        LeadAttempt.objects.create(ip=ip)

        since = timezone.now() - timedelta(days=1)
        attempts = LeadAttempt.objects.filter(ip=ip, created_at__gte=since).count()

        # 1. Чёрный список.
        if BlockedIP.objects.filter(ip=ip, is_active=True).exists():
            return Response(
                {"detail": "Доступ с вашего IP ограничен."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 2. Явный абьюз (много попыток) → в чёрный список.
        if attempts >= settings.LEAD_BLACKLIST_THRESHOLD:
            BlockedIP.objects.get_or_create(
                ip=ip, defaults={"reason": "Подозрительная активность (много попыток за сутки)"}
            )
            return Response(
                {"detail": "Доступ с вашего IP ограничен."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 3. Rate-limit: не более N заявок в сутки с одного IP.
        recent = Lead.objects.filter(ip=ip, created_at__gte=since).count()
        if recent >= settings.LEAD_RATE_LIMIT_PER_DAY:
            return Response(
                {"detail": "Слишком много заявок с вашего IP. Попробуйте позже."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # 4. Капча на повторную отправку с одного IP.
        if recent >= 1 and not verify_smartcaptcha(request.data.get("smart_token", ""), ip):
            return Response(
                {"detail": "captcha_required", "code": "captcha_required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        lead = serializer.save()
        lead.ip = get_client_ip(self.request)
        lead.source = self.request.META.get("HTTP_REFERER", "")
        lead.save(update_fields=["ip", "source"])
        notify_lead(lead)


class ContactCreateView(LeadCreateView):
    serializer_class = ContactSerializer


class CallbackCreateView(LeadCreateView):
    serializer_class = CallbackSerializer


class OrderServiceCreateView(LeadCreateView):
    serializer_class = OrderServiceSerializer


class BriefCreateView(LeadCreateView):
    serializer_class = BriefSerializer


class ConsultationCreateView(LeadCreateView):
    serializer_class = ConsultationSerializer


class SubscribeCreateView(LeadCreateView):
    serializer_class = SubscribeSerializer


class BudgetRangeListView(generics.ListAPIView):
    serializer_class = BudgetRangeSerializer
    queryset = BudgetRange.objects.all()
    pagination_class = None
