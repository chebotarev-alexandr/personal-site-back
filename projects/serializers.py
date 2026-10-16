"""Serializers for the projects app."""

from rest_framework import serializers

from .models import Project, ProjectImage, ProjectTag


class ProjectTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTag
        fields = ["id", "name", "slug"]


class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ["id", "image", "alt"]


class ProjectSerializer(serializers.ModelSerializer):
    tags = ProjectTagSerializer(many=True, read_only=True)
    images = ProjectImageSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "slug",
            "client",
            "short_description",
            "description",
            "year",
            "cover",
            "url",
            "repository_url",
            "tags",
            "stack",
            "results",
            "is_featured",
            "images",
        ]
