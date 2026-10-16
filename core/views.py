"""Views for the core app."""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AboutSection, HeroSection, SiteSettings, SocialLink, Stat
from .serializers import SiteSerializer


class SiteView(APIView):
    """Aggregated site chrome: settings + hero + about + stats + socials."""

    def get(self, request):
        data = {
            "settings": SiteSettings.load(),
            "hero": HeroSection.load(),
            "about": AboutSection.load(),
            "stats": Stat.objects.filter(is_active=True),
            "socials": SocialLink.objects.filter(is_active=True),
        }
        serializer = SiteSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
