from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("chat/messages/", views.ChatMessageCreateView.as_view(), name="chat-message-create"),
    path("chat/<uuid:uid>/messages/", views.ChatMessagesView.as_view(), name="chat-messages"),
    path("chat/<uuid:uid>/reply/", views.ChatReplyView.as_view(), name="chat-reply"),
]
