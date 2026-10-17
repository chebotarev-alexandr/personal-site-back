"""Serializers and views for blog posts."""

from rest_framework import serializers, viewsets

from common.fields import RelativeImageField

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    cover = RelativeImageField()

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "excerpt",
            "content",
            "cover",
            "tags",
            "reading_time",
            "published_at",
        ]


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PostSerializer
    lookup_field = "slug"
    search_fields = ["title", "excerpt", "content"]
    ordering = ["-published_at"]

    def get_queryset(self):
        return Post.objects.filter(is_published=True)
