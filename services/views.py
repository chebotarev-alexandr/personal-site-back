"""Views for the services app."""

from rest_framework import generics, viewsets

from .models import PricingPlan, ProcessStep, Service, ServiceCategory, Technology
from .serializers import (
    PricingPlanSerializer,
    ProcessStepSerializer,
    ServiceCategorySerializer,
    ServiceSerializer,
    TechnologySerializer,
)


class ServiceCategoryListView(generics.ListAPIView):
    serializer_class = ServiceCategorySerializer
    queryset = ServiceCategory.objects.filter(is_active=True)
    pagination_class = None


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ServiceSerializer
    lookup_field = "slug"
    filterset_fields = ["category__slug", "is_featured"]
    search_fields = ["title", "short_description"]
    ordering_fields = ["sort_order", "title"]
    ordering = ["sort_order"]

    def get_queryset(self):
        return Service.objects.filter(is_active=True, category__is_active=True).select_related("category")


class TechnologyListView(generics.ListAPIView):
    serializer_class = TechnologySerializer
    queryset = Technology.objects.filter(is_active=True)
    pagination_class = None


class PricingPlanListView(generics.ListAPIView):
    serializer_class = PricingPlanSerializer
    queryset = PricingPlan.objects.filter(is_active=True).select_related("service")
    pagination_class = None


class ProcessStepListView(generics.ListAPIView):
    serializer_class = ProcessStepSerializer
    queryset = ProcessStep.objects.filter(is_active=True)
    pagination_class = None
