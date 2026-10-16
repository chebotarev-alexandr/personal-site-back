"""Services: categories, services, technologies, pricing plans, process steps."""

from django.db import models

from common.models import ActiveModel, SortableModel, TimeStampedModel


class ServiceCategory(SortableModel, ActiveModel):
    """A group of services (e.g. «Веб-разработка», «Интеграции»)."""

    name = models.CharField("Название", max_length=120)
    slug = models.SlugField("Slug", max_length=140, unique=True)
    description = models.TextField("Описание", blank=True)
    icon = models.CharField("Иконка", max_length=64, blank=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Категория услуг"
        verbose_name_plural = "Категории услуг"

    def __str__(self) -> str:
        return self.name


class Service(SortableModel, ActiveModel, TimeStampedModel):
    """A sellable service with pricing, features and tech stack."""

    class PriceType(models.TextChoices):
        FIXED = "fixed", "Фиксированная цена"
        FROM = "from", "От (минимальная)"
        NEGOTIABLE = "negotiable", "По договорённости"

    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="services",
        verbose_name="Категория",
    )
    title = models.CharField("Название", max_length=160)
    slug = models.SlugField("Slug", max_length=180, unique=True)
    short_description = models.CharField("Короткое описание", max_length=255)
    description = models.TextField("Полное описание", blank=True)
    icon = models.CharField("Иконка", max_length=64, blank=True)
    image = models.ImageField("Изображение", upload_to="services/", blank=True, null=True)

    price = models.DecimalField("Цена (фиксированная)", max_digits=12, decimal_places=2, null=True, blank=True)
    price_from = models.DecimalField("Цена от", max_digits=12, decimal_places=2, null=True, blank=True)
    price_type = models.CharField(
        "Тип цены",
        max_length=12,
        choices=PriceType.choices,
        default=PriceType.FROM,
    )
    duration = models.CharField("Срок (например «2–4 недели»)", max_length=120, blank=True)

    features = models.JSONField("Что входит (список)", default=list, blank=True)
    stack = models.JSONField("Стек технологий (список)", default=list, blank=True)

    is_featured = models.BooleanField("Показывать на главной", default=False, db_index=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self) -> str:
        return self.title


class Technology(SortableModel, ActiveModel):
    """A technology in the stack (backend/frontend/db/devops...)."""

    class Category(models.TextChoices):
        BACKEND = "backend", "Backend"
        FRONTEND = "frontend", "Frontend"
        DATABASE = "database", "Базы данных"
        DEVOPS = "devops", "DevOps / Инфраструктура"
        MOBILE = "mobile", "Mobile"
        OTHER = "other", "Другое"

    name = models.CharField("Название", max_length=80)
    icon = models.CharField("Иконка", max_length=64, blank=True)
    category = models.CharField("Категория", max_length=20, choices=Category.choices, default=Category.OTHER)
    proficiency = models.PositiveSmallIntegerField("Владение, %", default=80, help_text="0–100")

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Технология"
        verbose_name_plural = "Технологии"

    def __str__(self) -> str:
        return self.name


class PricingPlan(SortableModel, ActiveModel):
    """A pricing package (e.g. «Лендинг», «Сайт под ключ», «Поддержка»)."""

    name = models.CharField("Название", max_length=120)
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField("Валюта", max_length=8, default="₽")
    period = models.CharField("Период (например «/мес» или «разово»)", max_length=40, blank=True)
    badge = models.CharField("Бейдж (например «Популярный»)", max_length=60, blank=True)
    description = models.CharField("Описание", max_length=255, blank=True)
    features = models.JSONField("Что входит (список)", default=list, blank=True)
    is_popular = models.BooleanField("Популярный тариф", default=False, db_index=True)
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="plans",
        verbose_name="Связанная услуга",
    )

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Тариф"
        verbose_name_plural = "Тарифы"

    def __str__(self) -> str:
        return self.name


class ProcessStep(SortableModel, ActiveModel):
    """A step in the «как я работаю» workflow."""

    title = models.CharField("Заголовок", max_length=160)
    description = models.TextField("Описание", blank=True)
    icon = models.CharField("Иконка", max_length=64, blank=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Этап работы"
        verbose_name_plural = "Этапы работы"

    def __str__(self) -> str:
        return self.title
