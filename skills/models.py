"""Skills grouped into categories (languages, frameworks, tools...)."""

from django.db import models

from common.models import ActiveModel, SortableModel


class SkillGroup(SortableModel, ActiveModel):
    name = models.CharField("Название группы", max_length=120)
    icon = models.CharField("Иконка", max_length=64, blank=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Группа навыков"
        verbose_name_plural = "Группы навыков"

    def __str__(self) -> str:
        return self.name


class Skill(SortableModel, ActiveModel):
    group = models.ForeignKey(SkillGroup, on_delete=models.CASCADE, related_name="skills", verbose_name="Группа")
    name = models.CharField("Название", max_length=120)
    level = models.PositiveSmallIntegerField("Уровень, %", default=80, help_text="0–100")
    years = models.DecimalField("Лет опыта", max_digits=4, decimal_places=1, null=True, blank=True)
    icon = models.CharField("Иконка", max_length=64, blank=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"

    def __str__(self) -> str:
        return self.name
