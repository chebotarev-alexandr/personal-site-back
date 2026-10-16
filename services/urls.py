"""URL routes for the services app."""

from django.urls import path

from .views import (
    PricingPlanListView,
    ProcessStepListView,
    ServiceCategoryListView,
    ServiceViewSet,
    TechnologyListView,
)

app_name = "services"

urlpatterns = [
    path("services/", ServiceViewSet.as_view({"get": "list"}), name="service-list"),
    path("services/categories/", ServiceCategoryListView.as_view(), name="category-list"),
    path("services/<slug:slug>/", ServiceViewSet.as_view({"get": "retrieve"}), name="service-detail"),
    path("technologies/", TechnologyListView.as_view(), name="technology-list"),
    path("pricing/", PricingPlanListView.as_view(), name="pricing-list"),
    path("process/", ProcessStepListView.as_view(), name="process-list"),
]
