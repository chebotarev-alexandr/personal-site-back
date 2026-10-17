"""Serializers and views for testimonials."""

from rest_framework import generics, serializers

from common.fields import RelativeImageField

from .models import Testimonial


class TestimonialSerializer(serializers.ModelSerializer):
    photo = RelativeImageField()

    class Meta:
        model = Testimonial
        fields = ["id", "author", "position", "company", "photo", "text", "rating"]


class TestimonialListView(generics.ListAPIView):
    serializer_class = TestimonialSerializer
    queryset = Testimonial.objects.filter(is_active=True)
    pagination_class = None
