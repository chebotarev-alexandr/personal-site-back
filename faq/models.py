"""FAQ categories and items."""

from django.db import models

from common.models import ActiveModel, SortableModel


class FAQCategory(SortableModel, ActiveModel):
    name = models.CharField("Название категории", max_length=120)
    slug = models.SlugField("Slug", max_length=140, unique=True)
    icon = models.CharField("Иконка", max_length=64, blank=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Категория FAQ"
        verbose_name_plural = "Категории FAQ"

    def __str__(self) -> str:
        return self.name


class FAQItem(SortableModel, ActiveModel):
    category = models.ForeignKey(
        FAQCategory,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Категория",
    )
    question = models.CharField("Вопрос", max_length=255)
    answer = models.TextField("Ответ")

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Вопрос-ответ"
        verbose_name_plural = "Вопросы-ответы"

    def __str__(self) -> str:
        return self.question
