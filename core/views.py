"""Views for the core app: aggregated site config + SEO (sitemap, robots)."""

from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from blog.models import Post
from projects.models import Project
from services.models import Service

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


def _base_url(request) -> str:
    scheme = "https" if request.is_secure() else "http"
    return f"{scheme}://{request.get_host()}"


def robots_view(request) -> HttpResponse:
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {_base_url(request)}/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")


def sitemap_view(request) -> HttpResponse:
    base = _base_url(request)
    entries = [
        (f"{base}/", None, "monthly", "1.0"),
        (f"{base}/services/", None, "weekly", "0.9"),
        (f"{base}/projects/", None, "weekly", "0.9"),
        (f"{base}/about/", None, "monthly", "0.8"),
        (f"{base}/blog/", None, "weekly", "0.8"),
        (f"{base}/faq/", None, "monthly", "0.7"),
        (f"{base}/contact/", None, "monthly", "0.8"),
    ]
    for service in Service.objects.filter(is_active=True):
        entries.append((f"{base}/services/{service.slug}/", None, "weekly", "0.7"))
    for project in Project.objects.filter(is_active=True):
        entries.append((f"{base}/projects/{project.slug}/", None, "weekly", "0.7"))
    for post in Post.objects.filter(is_published=True):
        entries.append((f"{base}/blog/{post.slug}/", post.published_at, "weekly", "0.6"))

    parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for loc, lastmod, changefreq, priority in entries:
        parts.append("  <url>")
        parts.append(f"    <loc>{loc}</loc>")
        if lastmod:
            parts.append(f"    <lastmod>{lastmod.isoformat()}</lastmod>")
        parts.append(f"    <changefreq>{changefreq}</changefreq>")
        parts.append(f"    <priority>{priority}</priority>")
        parts.append("  </url>")
    parts.append("</urlset>")
    return HttpResponse("\n".join(parts), content_type="application/xml")
