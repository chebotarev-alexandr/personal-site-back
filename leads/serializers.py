"""Serializers for lead/request forms.

Each form type is a dedicated serializer enforcing its own required fields.
``request_type`` is a class attribute set here — never accepted from the
client — so a forged payload cannot change the lead's type.
"""

from rest_framework import serializers

from common.validators import validate_phone
from services.models import Service

from .models import BudgetRange, Lead


class LeadSerializer(serializers.Serializer):
    """Base for all lead forms: injects the lead type on create."""

    request_type: str = Lead.Type.CONTACT

    def create(self, validated_data):
        validated_data["type"] = self.request_type
        return Lead.objects.create(**validated_data)


class ContactSerializer(LeadSerializer):
    request_type = Lead.Type.CONTACT

    name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, validators=[validate_phone])
    message = serializers.CharField(required=False, allow_blank=True)


class CallbackSerializer(LeadSerializer):
    request_type = Lead.Type.CALLBACK

    name = serializers.CharField(max_length=120)
    phone = serializers.CharField(max_length=32, validators=[validate_phone])
    message = serializers.CharField(required=False, allow_blank=True)


class OrderServiceSerializer(LeadSerializer):
    request_type = Lead.Type.ORDER_SERVICE

    name = serializers.CharField(max_length=120)
    phone = serializers.CharField(max_length=32, validators=[validate_phone])
    email = serializers.EmailField(required=False, allow_blank=True)
    service = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Service.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    message = serializers.CharField(required=False, allow_blank=True)


class BriefSerializer(LeadSerializer):
    request_type = Lead.Type.PROJECT_BRIEF

    name = serializers.CharField(max_length=120)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, validators=[validate_phone])
    company = serializers.CharField(max_length=160, required=False, allow_blank=True)
    service = serializers.SlugRelatedField(
        slug_field="slug",
        queryset=Service.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    budget = serializers.PrimaryKeyRelatedField(queryset=BudgetRange.objects.all(), required=False, allow_null=True)
    deadline = serializers.CharField(max_length=120, required=False, allow_blank=True)
    message = serializers.CharField(required=False, allow_blank=True)


class ConsultationSerializer(LeadSerializer):
    request_type = Lead.Type.CONSULTATION

    name = serializers.CharField(max_length=120)
    phone = serializers.CharField(max_length=32, validators=[validate_phone])
    message = serializers.CharField(required=False, allow_blank=True)


class SubscribeSerializer(LeadSerializer):
    request_type = Lead.Type.SUBSCRIPTION

    email = serializers.EmailField()


class BudgetRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetRange
        fields = ["id", "label"]
