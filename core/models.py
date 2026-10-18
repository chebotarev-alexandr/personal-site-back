"""Site-wide content: settings, hero, about, stats, social links.

Everything here is editable from the Django admin and served through the
public API — no hardcoded content in the frontend.
"""

from django.db import models

from common.models import ActiveModel, SingletonModel, SortableModel, TimeStampedModel


class SiteSettings(SingletonModel, TimeStampedModel):
    """Single-row site configuration (contacts, SEO, analytics, branding)."""

    site_name = models.CharField("Название сайта", max_length=120, default="Мой сайт")
    tagline = models.CharField("Слоган", max_length=255, blank=True)
    description = models.TextField("Краткое описание (для SEO)", blank=True)
    keywords = models.CharField("Ключевые слова (через запятую)", max_length=500, blank=True)

    logo = models.ImageField("Логотип", upload_to="site/", blank=True, null=True)
    favicon = models.ImageField("Favicon", upload_to="site/", blank=True, null=True)

    # Contacts
    email = models.EmailField("Email", blank=True)
    phone = models.CharField("Телефон", max_length=32, blank=True)
    telegram = models.CharField("Telegram (ссылка или username)", max_length=255, blank=True)
    whatsapp = models.CharField("WhatsApp (ссылка)", max_length=255, blank=True)
    city = models.CharField("Город", max_length=120, blank=True)
    address = models.CharField("Адрес", max_length=255, blank=True)
    work_hours = models.CharField("Часы работы", max_length=120, blank=True)

    # Branding / design tokens applied by the frontend at runtime
    accent_color = models.CharField("Акцентный цвет (hex)", max_length=9, default="#6366f1")

    # Footer
    footer_description = models.TextField("Описание в подвале", blank=True)
    copyright_text = models.CharField("Текст копирайта", max_length=255, blank=True)

    # SEO / analytics
    meta_title = models.CharField("Meta title (если пусто — site_name)", max_length=255, blank=True)
    meta_description = models.CharField("Meta description", max_length=255, blank=True)
    analytics_code = models.TextField("Код аналитики (Yandex.Metrika / GA)", blank=True)

    # Уведомления о новых заявках (Telegram)
    telegram_alerts_enabled = models.BooleanField("Telegram-уведомления включены", default=True)
    telegram_bot_token = models.CharField("Telegram: токен бота", max_length=255, blank=True)
    telegram_chat_id = models.CharField("Telegram: chat_id для уведомлений", max_length=120, blank=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self) -> str:
        return self.site_name


class SocialLink(SortableModel, ActiveModel):
    """A link to a social profile / messenger, editable from the admin."""

    class Platform(models.TextChoices):
        TELEGRAM = "telegram", "Telegram"
        WHATSAPP = "whatsapp", "WhatsApp"
        GITHUB = "github", "GitHub"
        LINKEDIN = "linkedin", "LinkedIn"
        VK = "vk", "VK"
        HABR = "habr", "Habr"
        YOUTUBE = "youtube", "YouTube"
        TWITTER = "twitter", "X / Twitter"
        EMAIL = "email", "Email"
        OTHER = "other", "Другое"

    platform = models.CharField("Платформа", max_length=20, choices=Platform.choices)
    label = models.CharField("Подпись", max_length=120, blank=True)
    url = models.URLField("Ссылка")
    icon = models.CharField("Иконка (svg-класс)", max_length=64, blank=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Социальная сеть"
        verbose_name_plural = "Социальные сети"

    def __str__(self) -> str:
        return self.label or self.get_platform_display()


class HeroSection(SingletonModel, TimeStampedModel):
    """First screen of the landing page."""

    eyebrow = models.CharField("Надзаголовок", max_length=120, blank=True)
    title = models.CharField("Заголовок", max_length=255, default="Разрабатываю цифровые продукты")
    subtitle = models.CharField("Подзаголовок", max_length=255, blank=True)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Фото/изображение", upload_to="site/", blank=True, null=True)
    typed_words = models.JSONField("Слова для печатающегося эффекта", default=list, blank=True)

    primary_btn_text = models.CharField("Текст основной кнопки", max_length=64, default="Обсудить проект")
    primary_btn_url = models.CharField("Ссылка основной кнопки", max_length=255, default="#contact")
    secondary_btn_text = models.CharField("Текст вторичной кнопки", max_length=64, blank=True)
    secondary_btn_url = models.CharField("Ссылка вторичной кнопки", max_length=255, blank=True)

    class Meta:
        verbose_name = "Первый экран"
        verbose_name_plural = "Первый экран"

    def __str__(self) -> str:
        return self.title


class Stat(SortableModel, ActiveModel):
    """A single number/stat shown on the landing (years, projects, clients...)."""

    value = models.CharField("Значение", max_length=32, help_text="Например: 5+")
    label = models.CharField("Подпись", max_length=120)
    icon = models.CharField("Иконка", max_length=64, blank=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Показатель"
        verbose_name_plural = "Показатели"

    def __str__(self) -> str:
        return f"{self.value} — {self.label}"


class AboutSection(SingletonModel, TimeStampedModel):
    """ "About me" block on the landing."""

    title = models.CharField("Заголовок", max_length=255, default="Обо мне")
    lead = models.CharField("Лид (короткая строка)", max_length=255, blank=True)
    text = models.TextField("Основной текст", blank=True)
    image = models.ImageField("Фото", upload_to="site/", blank=True, null=True)
    resume_url = models.URLField("Ссылка на резюме", blank=True)
    highlights = models.JSONField("Ключевые пункты (список)", default=list, blank=True)

    class Meta:
        verbose_name = "Блок «Обо мне»"
        verbose_name_plural = "Блок «Обо мне»"

    def __str__(self) -> str:
        return self.title
