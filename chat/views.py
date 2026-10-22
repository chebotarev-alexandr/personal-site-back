"""Chat API: send visitor messages, poll messages, and accept owner replies."""

import uuid

from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.utils import get_client_ip

from .models import ChatMessage, ChatSession
from .notify import notify_chat_message
from .serializers import ChatMessageSerializer

MAX_MESSAGE_LEN = 2000


def _get_session(uid: str):
    try:
        return ChatSession.objects.get(uid=uuid.UUID(str(uid)), is_open=True)
    except (ChatSession.DoesNotExist, ValueError, TypeError):
        return None


class ChatMessageCreateView(APIView):
    """Send a visitor message; creates the session on the first message."""

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"detail": "Сообщение пустое."}, status=status.HTTP_400_BAD_REQUEST)
        if len(text) > MAX_MESSAGE_LEN:
            return Response({"detail": "Сообщение слишком длинное."}, status=status.HTTP_400_BAD_REQUEST)

        session = _get_session(request.data.get("uid") or "")
        if session is None:
            session = ChatSession.objects.create(ip=get_client_ip(request))

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
