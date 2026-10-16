"""Admin configuration for the services app."""

from django.contrib import admin

from .models import PricingPlan, ProcessStep, Service, ServiceCategory, Technology


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price_type", "price_from", "is_featured", "sort_order", "is_active")
    list_editable = ("is_featured", "sort_order", "is_active")
    list_filter = ("category", "price_type", "is_featured", "is_active")
    search_fields = ("title", "short_description", "description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ()
    fieldsets = (
        ("Основное", {"fields": ("category", "title", "slug", "short_description", "description", "icon", "image")}),
        ("Цена и сроки", {"fields": ("price_type", "price", "price_from", "duration")}),
        ("Состав", {"fields": ("features", "stack")}),
        ("Отображение", {"fields": ("is_featured", "sort_order", "is_active")}),
    )


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "proficiency", "sort_order", "is_active")
    list_editable = ("category", "proficiency", "sort_order", "is_active")
    list_filter = ("category", "is_active")


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "period", "is_popular", "sort_order", "is_active")
    list_editable = ("is_popular", "sort_order", "is_active")
    list_filter = ("is_popular", "is_active")


@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("is_active",)
