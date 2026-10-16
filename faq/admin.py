"""Admin configuration for FAQ."""

from django.contrib import admin

from .models import FAQCategory, FAQItem


class FAQItemInline(admin.TabularInline):
    model = FAQItem
    extra = 0
    fields = ("question", "answer", "sort_order", "is_active")


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [FAQItemInline]
