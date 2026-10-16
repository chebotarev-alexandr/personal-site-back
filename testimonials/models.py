"""Client testimonials."""

from django.db import models

from common.models import ActiveModel, SortableModel, TimeStampedModel


class Testimonial(SortableModel, ActiveModel, TimeStampedModel):
    author = models.CharField("Автор", max_length=120)
    position = models.CharField("Должность", max_length=120, blank=True)
    company = models.CharField("Компания", max_length=160, blank=True)
    photo = models.ImageField("Фото", upload_to="testimonials/", blank=True, null=True)
    text = models.TextField("Текст отзыва")
    rating = models.PositiveSmallIntegerField("Оценка (1–5)", default=5)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="testimonials",
        verbose_name="Связанный проект",
    )

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self) -> str:
        return f"{self.author} — {self.company or self.position}"
