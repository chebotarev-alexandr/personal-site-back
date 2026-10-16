"""URL routes for the requests (leads) app."""

from django.urls import path

from .views import (
    BriefCreateView,
    BudgetRangeListView,
    CallbackCreateView,
    ConsultationCreateView,
    ContactCreateView,
    OrderServiceCreateView,
    SubscribeCreateView,
)

app_name = "leads"

urlpatterns = [
    path("requests/contact/", ContactCreateView.as_view(), name="contact"),
    path("requests/callback/", CallbackCreateView.as_view(), name="callback"),
    path("requests/order/", OrderServiceCreateView.as_view(), name="order"),
    path("requests/brief/", BriefCreateView.as_view(), name="brief"),
    path("requests/consultation/", ConsultationCreateView.as_view(), name="consultation"),
    path("requests/subscribe/", SubscribeCreateView.as_view(), name="subscribe"),
    path("requests/budgets/", BudgetRangeListView.as_view(), name="budgets"),
]
