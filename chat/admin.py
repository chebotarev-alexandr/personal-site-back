"""Admin for the chat app (view/close sessions and read messages)."""

from django.contrib import admin

from .models import ChatMessage, ChatSession


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("direction", "text", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("uid_short", "ip", "is_open", "created_at", "updated_at")
    list_filter = ("is_open", "created_at")
    search_fields = ("uid", "ip")
    readonly_fields = ("uid", "ip", "created_at", "updated_at")
    inlines = [ChatMessageInline]
    actions = ["close_sessions"]

    @admin.display(description="Сессия")
    def uid_short(self, obj):
        return obj.uid.hex[:8]

    @admin.action(description="Закрыть выбранные сессии")
    def close_sessions(self, request, queryset):
        queryset.update(is_open=False)
