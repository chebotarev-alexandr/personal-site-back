"""URL routes for the core app."""

from django.urls import path

from .views import SiteView

app_name = "core"

urlpatterns = [
    path("site/", SiteView.as_view(), name="site"),
]
