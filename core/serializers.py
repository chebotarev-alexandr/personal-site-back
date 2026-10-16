"""Serializers for the core app (site config, hero, about, stats, socials)."""

from rest_framework import serializers

from .models import AboutSection, HeroSection, SiteSettings, SocialLink, Stat


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = [
            "site_name",
            "tagline",
            "description",
            "keywords",
            "logo",
            "favicon",
            "email",
            "phone",
            "telegram",
            "whatsapp",
            "city",
            "address",
            "work_hours",
            "accent_color",
            "footer_description",
            "copyright_text",
            "meta_title",
            "meta_description",
            "analytics_code",
        ]


class SocialLinkSerializer(serializers.ModelSerializer):
    platform_label = serializers.CharField(source="get_platform_display", read_only=True)

    class Meta:
        model = SocialLink
        fields = ["id", "platform", "platform_label", "label", "url", "icon"]


class HeroSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSection
        fields = [
            "eyebrow",
            "title",
            "subtitle",
            "description",
            "image",
            "typed_words",
            "primary_btn_text",
            "primary_btn_url",
            "secondary_btn_text",
            "secondary_btn_url",
        ]


class AboutSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutSection
        fields = ["title", "lead", "text", "image", "resume_url", "highlights"]


class StatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stat
        fields = ["id", "value", "label", "icon"]


class SiteSerializer(serializers.Serializer):
    """Aggregated payload for the landing page — one request for all site chrome."""

    settings = SiteSettingsSerializer(read_only=True)
    hero = HeroSerializer(read_only=True)
    about = AboutSerializer(read_only=True)
    stats = StatSerializer(many=True, read_only=True)
    socials = SocialLinkSerializer(many=True, read_only=True)
