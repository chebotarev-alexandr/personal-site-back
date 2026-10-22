"""Admin configuration for blog."""

from django.contrib import admin
from django.db import models

from core.widgets import MarkdownEditorWidget

from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_at", "reading_time", "created_at")
    list_editable = ("is_published",)
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    formfield_overrides = {
        models.TextField: {"widget": MarkdownEditorWidget},
    }
    fieldsets = (
        ("Основное", {"fields": ("title", "slug", "excerpt", "content", "tags")}),
        ("Медиа", {"fields": ("cover",)}),
        ("Публикация", {"fields": ("reading_time", "published_at", "is_published", "sort_order")}),
    )
