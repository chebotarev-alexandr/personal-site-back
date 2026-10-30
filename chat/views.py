"""Chat API: send visitor messages, poll messages, and accept owner replies."""

import uuid
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import get_client_ip
from leads.captcha import verify_smartcaptcha
from leads.models import BlockedIP

from .models import ChatAttempt, ChatMessage, ChatSession
from .notify import notify_chat_message
from .serializers import ChatMessageSerializer

MAX_MESSAGE_LEN = 2000


def _get_session(uid: str):
    try:
        return ChatSession.objects.get(uid=uuid.UUID(str(uid)), is_open=True)
    except (ChatSession.DoesNotExist, ValueError, TypeError):
        return None


class ChatMessageCreateView(APIView):
    """Отправка сообщения посетителя; сессия создаётся на первом сообщении.

    Антиспам: rate-limit по IP за короткое окно → Яндекс SmartCaptcha → при
    накоплении попыток за час — блокировка IP (nginx-чёрный список).
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ip = get_client_ip(request)
        now = timezone.now()

        # Фиксируем КАЖДУЮ попытку (даже отклонённую) — иначе порог блокировки
        # был бы недостижим: неуспешные POST'ы не создают сообщений.
        ChatAttempt.objects.create(ip=ip)

        # 1. Уже в чёрном списке.
        if BlockedIP.objects.filter(ip=ip, is_active=True).exists():
            return Response(
                {"detail": "Доступ с вашего IP ограничен."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 2. Слишком много попыток за час → блокировка IP.
        hour_ago = now - timedelta(hours=1)
        attempts = ChatAttempt.objects.filter(ip=ip, created_at__gte=hour_ago).count()
        if attempts >= settings.CHAT_BLACKLIST_THRESHOLD:
            BlockedIP.objects.get_or_create(
                ip=ip, defaults={"reason": "Спам в чате (много попыток)"}
            )
            return Response(
                {"detail": "Доступ с вашего IP ограничен."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 3. Текст сообщения.
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"detail": "Сообщение пустое."}, status=status.HTTP_400_BAD_REQUEST)
        if len(text) > MAX_MESSAGE_LEN:
            return Response({"detail": "Сообщение слишком длинное."}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Имя (обязательно при первом сообщении), контакт — опционально.
        name = (request.data.get("name") or "").strip()[:120]
        contact = (request.data.get("contact") or "").strip()[:255]

        session = _get_session(request.data.get("uid") or "")
        if session is None:
            if not name:
                return Response({"detail": "Укажите ваше имя."}, status=status.HTTP_400_BAD_REQUEST)
            session = ChatSession.objects.create(ip=ip, name=name, contact=contact)
        elif (name and name != session.name) or (contact and contact != session.contact):
            if name:
                session.name = name
            if contact:
                session.contact = contact
            session.save()

        # 5. Rate-limit за короткое окно → капча (с «льготой» после прохождения).
        window_ago = now - timedelta(seconds=settings.CHAT_SPAM_WINDOW_SECONDS)
        recent = ChatMessage.objects.filter(
            session__ip=ip,
            direction=ChatMessage.Direction.INCOMING,
            created_at__gte=window_ago,
        ).count()
        if recent >= settings.CHAT_SPAM_MAX_MESSAGES:
            passed = session.captcha_passed_at and (
                now - session.captcha_passed_at
            ) < timedelta(seconds=settings.CHAT_SPAM_WINDOW_SECONDS)
            if not passed:
                token = (request.data.get("smart_token") or "").strip()
                if not verify_smartcaptcha(token, ip):
                    return Response(
                        {
                            "detail": "Пройдите проверку «Я не робот» и отправьте сообщение ещё раз.",
                            "code": "captcha_required",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                session.captcha_passed_at = now
                session.save()

        # 6. Создать сообщение и уведомить владельца.
        message = ChatMessage.objects.create(
            session=session, direction=ChatMessage.Direction.INCOMING, text=text
        )
        session.save(update_fields=["updated_at"])
        notify_chat_message(session, message)

        response = Response(
            {"uid": str(session.uid), "message": ChatMessageSerializer(message).data},
            status=status.HTTP_201_CREATED,
        )
        response["Cache-Control"] = "no-store"
        return response


class ChatMessagesView(APIView):
    """List a session's messages — polled by the widget every few seconds.

    ``Cache-Control: no-store`` keeps nginx's proxy cache from swallowing the
    owner's replies (the site caches GET /api/ responses for 10 min by default).
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request, uid):
        session = _get_session(uid)
        if session is None:
            return Response({"detail": "Сессия не найдена."}, status=status.HTTP_404_NOT_FOUND)
        messages = ChatMessageSerializer(session.messages.all(), many=True).data
        response = Response({"uid": str(session.uid), "messages": messages})
        response["Cache-Control"] = "no-store"
        return response


class ChatReplyView(APIView):
    """The Telegram bridge pushes the owner's reply here (secret-authenticated)."""

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request, uid):
        secret = request.headers.get("X-Chat-Secret", "")
        if not secret or secret != getattr(settings, "CHAT_SECRET", ""):
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"detail": "Сообщение пустое."}, status=status.HTTP_400_BAD_REQUEST)
        if len(text) > MAX_MESSAGE_LEN:
            return Response({"detail": "Сообщение слишком длинное."}, status=status.HTTP_400_BAD_REQUEST)

        session = _get_session(uid)
        if session is None:
            return Response({"detail": "Сессия не найдена."}, status=status.HTTP_404_NOT_FOUND)

        message = ChatMessage.objects.create(
            session=session, direction=ChatMessage.Direction.OUTGOING, text=text
        )
        session.save(update_fields=["updated_at"])
        return Response(
            {"ok": True, "message": ChatMessageSerializer(message).data},
            status=status.HTTP_201_CREATED,
        )
