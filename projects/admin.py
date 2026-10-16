"""Admin configuration for the projects app."""

from django.contrib import admin

from .models import Project, ProjectImage, ProjectTag


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 0
    fields = ("image", "alt", "sort_order")


@admin.register(ProjectTag)
class ProjectTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order")
    list_editable = ("sort_order",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "year", "is_featured", "sort_order", "is_active")
    list_editable = ("is_featured", "sort_order", "is_active")
    list_filter = ("is_featured", "is_active", "tags", "year")
    search_fields = ("title", "short_description", "description", "client")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    inlines = [ProjectImageInline]
    fieldsets = (
        ("Основное", {"fields": ("title", "slug", "client", "year", "short_description", "description")}),
        ("Медиа и ссылки", {"fields": ("cover", "url", "repository_url")}),
        ("Состав", {"fields": ("tags", "stack", "results")}),
        ("Отображение", {"fields": ("is_featured", "sort_order", "is_active")}),
    )
