"""Views for lead capture and budget options."""

from rest_framework import generics

from .models import BudgetRange
from .notify import notify_lead
from .serializers import (
    BriefSerializer,
    BudgetRangeSerializer,
    CallbackSerializer,
    ConsultationSerializer,
    ContactSerializer,
    OrderServiceSerializer,
    SubscribeSerializer,
)


class LeadCreateView(generics.CreateAPIView):
    """Base for all lead endpoints: stamps ip/source and notifies."""

    def perform_create(self, serializer):
        lead = serializer.save()
        lead.ip = self._client_ip()
        lead.source = self.request.META.get("HTTP_REFERER", "")
        lead.save(update_fields=["ip", "source"])
        notify_lead(lead)

    def _client_ip(self) -> str:
        forwarded = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return self.request.META.get("REMOTE_ADDR", "")


class ContactCreateView(LeadCreateView):
    serializer_class = ContactSerializer


class CallbackCreateView(LeadCreateView):
    serializer_class = CallbackSerializer


class OrderServiceCreateView(LeadCreateView):
    serializer_class = OrderServiceSerializer


class BriefCreateView(LeadCreateView):
    serializer_class = BriefSerializer


class ConsultationCreateView(LeadCreateView):
    serializer_class = ConsultationSerializer


class SubscribeCreateView(LeadCreateView):
    serializer_class = SubscribeSerializer


class BudgetRangeListView(generics.ListAPIView):
    serializer_class = BudgetRangeSerializer
    queryset = BudgetRange.objects.all()
    pagination_class = None
