"""Admin configuration for testimonials."""

from django.contrib import admin

from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author", "company", "position", "rating", "sort_order", "is_active")
    list_editable = ("rating", "sort_order", "is_active")
    list_filter = ("rating", "is_active")
    search_fields = ("author", "company", "text")
