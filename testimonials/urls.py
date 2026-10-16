"""URL routes for testimonials."""

from django.urls import path

from .serializers import TestimonialListView

app_name = "testimonials"

urlpatterns = [
    path("testimonials/", TestimonialListView.as_view(), name="testimonial-list"),
]
