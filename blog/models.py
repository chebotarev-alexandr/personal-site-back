"""Blog posts."""

from django.db import models

from common.models import SortableModel, TimeStampedModel


class Post(SortableModel, TimeStampedModel):
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("Slug", max_length=220, unique=True)
    excerpt = models.CharField("Анонс", max_length=300, blank=True)
    content = models.TextField("Содержимое (Markdown/HTML)")
    cover = models.ImageField("Обложка", upload_to="blog/", blank=True, null=True)
    tags = models.JSONField("Теги (список)", default=list, blank=True)
    reading_time = models.PositiveSmallIntegerField("Время чтения, мин", default=5)
    published_at = models.DateTimeField("Дата публикации", null=True, blank=True)
    is_published = models.BooleanField("Опубликовано", default=False, db_index=True)

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-published_at", "-id"]

    def __str__(self) -> str:
        return self.title
