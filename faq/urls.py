"""URL routes for FAQ."""

from django.urls import path

from .serializers import FAQCategoryListView

app_name = "faq"

urlpatterns = [
    path("faq/", FAQCategoryListView.as_view(), name="faq-list"),
]
