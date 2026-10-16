"""Serializers and views for FAQ."""

from rest_framework import generics, serializers

from .models import FAQCategory, FAQItem


class FAQItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQItem
        fields = ["id", "question", "answer"]


class FAQCategorySerializer(serializers.ModelSerializer):
    items = FAQItemSerializer(many=True, read_only=True)

    class Meta:
        model = FAQCategory
        fields = ["id", "name", "slug", "icon", "items"]


class FAQCategoryListView(generics.ListAPIView):
    serializer_class = FAQCategorySerializer
    queryset = FAQCategory.objects.filter(is_active=True).prefetch_related("items")
    pagination_class = None
