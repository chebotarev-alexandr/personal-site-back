"""Admin configuration for skills."""

from django.contrib import admin

from .models import Skill, SkillGroup


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 0
    fields = ("name", "level", "years", "icon", "sort_order", "is_active")


@admin.register(SkillGroup)
class SkillGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    inlines = [SkillInline]
