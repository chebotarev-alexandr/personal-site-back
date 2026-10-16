"""Portfolio projects with tags and galleries."""

from django.db import models

from common.models import ActiveModel, SortableModel, TimeStampedModel


class ProjectTag(SortableModel):
    """A tag for grouping/filtering projects (e.g. «Django», «SPA», «API»)."""

    name = models.CharField("Название", max_length=80)
    slug = models.SlugField("Slug", max_length=100, unique=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Тег проекта"
        verbose_name_plural = "Теги проектов"

    def __str__(self) -> str:
        return self.name


class Project(SortableModel, ActiveModel, TimeStampedModel):
    """A portfolio case."""

    title = models.CharField("Название", max_length=160)
    slug = models.SlugField("Slug", max_length=180, unique=True)
    client = models.CharField("Клиент / заказчик", max_length=160, blank=True)
    short_description = models.CharField("Короткое описание", max_length=255)
    description = models.TextField("Полное описание", blank=True)
    year = models.PositiveSmallIntegerField("Год", null=True, blank=True)

    cover = models.ImageField("Обложка", upload_to="projects/", blank=True, null=True)
    url = models.URLField("Ссылка на проект", blank=True)
    repository_url = models.URLField("Ссылка на репозиторий", blank=True)

    tags = models.ManyToManyField(ProjectTag, related_name="projects", blank=True, verbose_name="Теги")
    stack = models.JSONField("Стек (список)", default=list, blank=True)
    results = models.JSONField("Результаты (список)", default=list, blank=True)

    is_featured = models.BooleanField("Показывать на главной", default=False, db_index=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self) -> str:
        return self.title


class ProjectImage(SortableModel):
    """An additional screenshot/photo for a project gallery."""

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images", verbose_name="Проект")
    image = models.ImageField("Изображение", upload_to="projects/")
    alt = models.CharField("Alt-текст", max_length=160, blank=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Изображение проекта"
        verbose_name_plural = "Изображения проекта"

    def __str__(self) -> str:
        return f"{self.project.title} — {self.alt or self.pk}"
