"""Admin configuration for the requests app."""

from django.contrib import admin

from .models import BudgetRange, Lead


@admin.register(BudgetRange)
class BudgetRangeAdmin(admin.ModelAdmin):
    list_display = ("label", "sort_order")
    list_editable = ("sort_order",)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        "type",
        "name",
        "email",
        "phone",
        "service",
        "status",
        "is_processed",
        "created_at",
    )
    list_filter = ("type", "status", "is_processed", "created_at")
    list_editable = ("status", "is_processed")
    search_fields = ("name", "email", "phone", "company", "message")
    readonly_fields = ("type", "ip", "source", "created_at", "updated_at")
    fieldsets = (
        ("Заявка", {"fields": ("type", "status", "is_processed", "admin_note")}),
        (
            "Контакт",
            {"fields": ("name", "email", "phone", "company")},
        ),
        ("Детали", {"fields": ("service", "budget", "deadline", "message")}),
        ("Служебное", {"fields": ("ip", "source", "created_at", "updated_at")}),
    )
    actions = ["mark_processed", "mark_spam"]

    @admin.action(description="Отметить обработанными")
    def mark_processed(self, request, queryset):
        queryset.update(is_processed=True, status=Lead.Status.COMPLETED)

    @admin.action(description="Пометить как спам")
    def mark_spam(self, request, queryset):
        queryset.update(status=Lead.Status.SPAM)
