"""Serializers and views for skills."""

from rest_framework import generics, serializers

from .models import Skill, SkillGroup


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name", "level", "years", "icon"]


class SkillGroupSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = SkillGroup
        fields = ["id", "name", "icon", "skills"]


class SkillGroupListView(generics.ListAPIView):
    serializer_class = SkillGroupSerializer
    queryset = SkillGroup.objects.filter(is_active=True).prefetch_related("skills")
    pagination_class = None
