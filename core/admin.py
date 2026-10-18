"""Admin configuration for the core app."""

from django.contrib import admin

from .models import AboutSection, HeroSection, SiteSettings, SocialLink, Stat


class SingletonAdmin(admin.ModelAdmin):
    """Admin for single-row blocks: no add/delete, just edit."""

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = (
        ("Основное", {"fields": ("site_name", "tagline", "description", "keywords")}),
        ("Брендинг", {"fields": ("logo", "favicon", "accent_color")}),
        ("Контакты", {"fields": ("email", "phone", "telegram", "whatsapp", "city", "address", "work_hours")}),
        ("Подвал", {"fields": ("footer_description", "copyright_text")}),
        ("SEO / аналитика", {"fields": ("meta_title", "meta_description", "analytics_code")}),
        ("Уведомления (Telegram)", {"fields": ("telegram_alerts_enabled", "telegram_bot_token", "telegram_chat_id")}),
    )


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("label", "platform", "url", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("platform", "is_active")
    search_fields = ("label", "url")


@admin.register(HeroSection)
class HeroSectionAdmin(SingletonAdmin):
    fieldsets = (
        ("Заголовки", {"fields": ("eyebrow", "title", "subtitle", "description", "typed_words")}),
        ("Изображение", {"fields": ("image",)}),
        ("Кнопки", {"fields": ("primary_btn_text", "primary_btn_url", "secondary_btn_text", "secondary_btn_url")}),
    )


@admin.register(AboutSection)
class AboutSectionAdmin(SingletonAdmin):
    fieldsets = (
        ("Текст", {"fields": ("title", "lead", "text", "highlights")}),
        ("Медиа", {"fields": ("image", "resume_url")}),
    )


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ("value", "label", "icon", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("is_active",)
