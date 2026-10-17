"""Shared DRF serializer fields."""

from rest_framework import serializers


class RelativeImageField(serializers.ImageField):
    """ImageField that always returns the relative MEDIA_URL path.

    DRF's default behaviour builds an absolute URL from the request host,
    which breaks when the SSR Node server fetches the backend directly (the
    host is then the internal Docker service name). A relative path
    (/media/...) resolves correctly both in the browser and in SSR HTML.
    """

    def to_representation(self, value):
        if not value:
            return None
        use_url = getattr(self, "use_url", True)
        if use_url:
            try:
                return value.url
            except AttributeError:
                return None
        return super().to_representation(value)
