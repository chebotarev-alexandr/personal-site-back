"""Serializers for the services app."""

from rest_framework import serializers

from common.fields import RelativeImageField

from .models import PricingPlan, ProcessStep, Service, ServiceCategory, Technology


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ["id", "name", "slug", "description", "icon"]


class ServiceSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer(read_only=True)
    category_slug = serializers.SlugRelatedField(source="category", slug_field="slug", read_only=True)
    price_type_label = serializers.CharField(source="get_price_type_display", read_only=True)
    image = RelativeImageField()

    class Meta:
        model = Service
        fields = [
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "icon",
            "image",
            "price",
            "price_from",
            "price_type",
            "price_type_label",
            "duration",
            "features",
            "stack",
            "is_featured",
            "category",
            "category_slug",
        ]


class TechnologySerializer(serializers.ModelSerializer):
    category_label = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Technology
        fields = ["id", "name", "icon", "category", "category_label", "proficiency"]


class PricingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingPlan
        fields = [
            "id",
            "name",
            "price",
            "currency",
            "period",
            "badge",
            "description",
            "features",
            "is_popular",
            "service",
        ]


class ProcessStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessStep
        fields = ["id", "title", "description", "icon"]
