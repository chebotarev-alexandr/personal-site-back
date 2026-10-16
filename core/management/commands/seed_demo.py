"""Seed the database with demo content.

Usage::

    python manage.py seed_demo

Idempotent — safe to run repeatedly; every row is upserted by a stable key.
All content is editable afterwards from the Django admin.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import Post
from core.models import AboutSection, HeroSection, SiteSettings, SocialLink, Stat
from faq.models import FAQCategory, FAQItem
from leads.models import BudgetRange
from projects.models import Project, ProjectTag
from services.models import (
    PricingPlan,
    ProcessStep,
    Service,
    ServiceCategory,
    Technology,
)
from skills.models import Skill, SkillGroup
from testimonials.models import Testimonial


class Command(BaseCommand):
    help = "Загружает демо-контент для персонального сайта."

    def handle(self, *args, **options):
        self._site()
        self._hero()
        self._about()
        self._stats()
        self._socials()
        self._categories_and_services()
        self._technologies()
        self._pricing()
        self._process()
        self._projects()
        self._skills()
        self._testimonials()
        self._faq()
        self._budgets()
        self._blog()
        self.stdout.write(self.style.SUCCESS("Демо-контент загружен."))

    def _site(self):
        SiteSettings.load()
        SiteSettings.objects.update_or_create(
            pk=1,
            defaults={
                "site_name": "Александр Чеботарев",
                "tagline": "Fullstack-разработчик",
                "description": (
                    "Разрабатываю веб-сервисы, API и автоматизацию под ключ: "
                    "Django, FastAPI, Angular, ClickHouse. Беру задачи от лендинга до "
                    "высоконагруженных систем телеметрии."
                ),
                "keywords": "разработка, django, fastapi, angular, backend, python, телеграм боты, clickhouse",
                "email": "elips6102@gmail.com",
                "phone": "",
                "telegram": "",
                "whatsapp": "",
                "city": "Хабаровск",
                "address": "Работаю удалённо по всему миру",
                "work_hours": "Пн–Пт, 10:00–19:00 (UTC+10)",
                "accent_color": "#6366f1",
                "footer_description": (
                    "Проектирую и разрабатываю веб-сервисы и автоматизацию, которые решают бизнес-задачи."
                ),
                "copyright_text": "© Александр Чеботарев, 2026",
                "meta_title": "Александр Чеботарев — разработка веб-сервисов и API",
                "meta_description": (
                    "Fullstack-разработчик: Django, FastAPI, Angular, ClickHouse. "
                    "Веб-сайты, API, телеграм-боты и автоматизация под ключ."
                ),
            },
        )

    def _hero(self):
        HeroSection.load()
        HeroSection.objects.update_or_create(
            pk=1,
            defaults={
                "eyebrow": "Fullstack-разработчик · Python / Angular",
                "title": "Разрабатываю продукты, которые продают и работают",
                "subtitle": "Веб-сервисы, API и автоматизация под ключ",
                "description": (
                    "Помогаю бизнесу и командам: от быстрого лендинга до "
                    "высоконагруженных систем телеметрии на ClickHouse. "
                    "Чистый код, прозрачные сроки, ответственность за результат."
                ),
                "typed_words": ["Django", "FastAPI", "Angular", "ClickHouse", "Telegram-боты"],
                "primary_btn_text": "Обсудить проект",
                "primary_btn_url": "#contact",
                "secondary_btn_text": "Смотреть услуги",
                "secondary_btn_url": "#services",
            },
        )

    def _about(self):
        AboutSection.load()
        AboutSection.objects.update_or_create(
            pk=1,
            defaults={
                "title": "Обо мне",
                "lead": "Программирую, потому что люблю решать сложные задачи.",
                "text": (
                    "Более 5 лет разрабатываю серверные и клиентские части приложений. "
                    "Основной стек — Python (Django, FastAPI) и Angular, также изучаю Go. "
                    "Работал над системами спутниковой телеметрии: CAN-логи, "
                    "Redis Streams → ClickHouse → Grafana. Умею собирать продукт от идеи "
                    "до продакшена и поддерживать его."
                ),
                "highlights": [
                    "Полный цикл: аналитика → дизайн → код → деплой → поддержка",
                    "Опыт высоконагруженных систем телеметрии и аналитики",
                    "Понятная коммуникация и прозрачные сроки",
                    "Документация и чистый, поддерживаемый код",
                ],
            },
        )

    def _stats(self):
        stats = [
            {"value": "5+", "label": "лет опыта", "icon": "briefcase"},
            {"value": "30+", "label": "завершённых проектов", "icon": "rocket"},
            {"value": "20+", "label": "довольных клиентов", "icon": "users"},
            {"value": "99%", "label": "проектов сдано в срок", "icon": "check"},
        ]
        for order, data in enumerate(stats):
            Stat.objects.update_or_create(value=data["value"], defaults={**data, "sort_order": order})

    def _socials(self):
        socials = [
            {
                "platform": SocialLink.Platform.GITHUB,
                "label": "GitHub",
                "url": "https://github.com/chebotarev-alexandr",
                "sort_order": 1,
            },
            {
                "platform": SocialLink.Platform.EMAIL,
                "label": "Email",
                "url": "mailto:elips6102@gmail.com",
                "sort_order": 2,
            },
            {
                "platform": SocialLink.Platform.TELEGRAM,
                "label": "Telegram",
                "url": "https://t.me/your_username",
                "sort_order": 3,
            },
        ]
        for data in socials:
            SocialLink.objects.update_or_create(platform=data["platform"], defaults=data)

    def _categories_and_services(self):
        categories = {
            "web": ("Веб-разработка", "Сайты и веб-приложения"),
            "backend": ("Backend и API", "Серверная логика и интеграции"),
            "automation": ("Интеграции и автоматизация", "Боты, парсеры, интеграции"),
            "support": ("Сопровождение", "Поддержка и развитие продукта"),
        }
        cat_objs = {}
        for slug, (name, desc) in categories.items():
            cat_objs[slug], _ = ServiceCategory.objects.update_or_create(
                slug=slug, defaults={"name": name, "description": desc}
            )

        services = [
            # Web
            (
                "Лендинг",
                "landing",
                cat_objs["web"],
                30000,
                "1–2 недели",
                [
                    "Продающая структура и тексты",
                    "Адаптивная вёрстка",
                    "Формы заявок и аналитика",
                    "SEO-базовая оптимизация",
                ],
                ["Angular", "Tailwind", "Django"],
                True,
            ),
            (
                "Корпоративный сайт",
                "corporate-site",
                cat_objs["web"],
                80000,
                "3–4 недели",
                ["Уникальный дизайн", "CMS/админка для контента", "Мультиязычность", "Интеграция с CRM"],
                ["Angular", "Django", "PostgreSQL"],
                True,
            ),
            (
                "Интернет-магазин",
                "ecommerce",
                cat_objs["web"],
                120000,
                "4–8 недель",
                ["Каталог и корзина", "Оплата и доставка", "Личный кабинет", "Панель управления"],
                ["Angular", "Django", "PostgreSQL", "Redis"],
                False,
            ),
            (
                "Веб-приложение (SPA)",
                "spa",
                cat_objs["web"],
                150000,
                "от 6 недель",
                ["Проектирование архитектуры", "SPA на Angular", "REST API", "Деплой и мониторинг"],
                ["Angular", "Django/DRF", "PostgreSQL", "Docker"],
                True,
            ),
            # Backend
            (
                "Backend / REST API",
                "backend-api",
                cat_objs["backend"],
                100000,
                "от 4 недель",
                ["Проектирование схемы БД", "REST API с документацией", "Аутентификация и роли", "Тесты и CI"],
                ["Django/DRF", "FastAPI", "PostgreSQL", "Redis"],
                True,
            ),
            (
                "Телеграм-боты",
                "telegram-bots",
                cat_objs["backend"],
                25000,
                "1–2 недели",
                ["Сценарии и диалоги", "Интеграция с API и БД", "Платежи и рассылки", "Админ-панель"],
                ["Python", "aiogram", "PostgreSQL"],
                False,
            ),
            (
                "Парсеры и сбор данных",
                "parsers",
                cat_objs["backend"],
                40000,
                "1–3 недели",
                ["Сбор и нормализация данных", "Обработка и хранение", "Планировщик задач", "Экспорт в нужный формат"],
                ["Python", "Scrapy", "ClickHouse"],
                False,
            ),
            # Automation
            (
                "Интеграции (CRM, платежи, 1С)",
                "integrations",
                cat_objs["automation"],
                60000,
                "2–4 недели",
                ["Анализ API сторонних систем", "Синхронизация данных", "Обработка ошибок и логи", "Мониторинг"],
                ["Python", "Django", "Celery", "Redis"],
                False,
            ),
            # Support
            (
                "Техподдержка и доработка",
                "support",
                cat_objs["support"],
                15000,
                "ежемесячно",
                ["Исправление ошибок", "Доработки по задачам", "Обновление зависимостей", "Мониторинг и бэкапы"],
                ["Linux", "Docker", "Nginx", "Grafana"],
                False,
            ),
        ]
        for i, (title, slug, cat, price, duration, features, stack, featured) in enumerate(services):
            Service.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "category": cat,
                    "short_description": features[0] + " и другие задачи.",
                    "price_from": price,
                    "price_type": Service.PriceType.FROM,
                    "duration": duration,
                    "features": features,
                    "stack": stack,
                    "is_featured": featured,
                    "sort_order": i,
                },
            )

    def _technologies(self):
        techs = [
            ("Python", "backend", 95),
            ("Django", "backend", 90),
            ("FastAPI", "backend", 85),
            ("Go (изучаю)", "backend", 40),
            ("JavaScript/TypeScript", "frontend", 85),
            ("Angular", "frontend", 85),
            ("HTML/CSS/Tailwind", "frontend", 90),
            ("PostgreSQL", "database", 90),
            ("ClickHouse", "database", 80),
            ("Redis", "database", 85),
            ("InfluxDB", "database", 70),
            ("Docker", "devops", 85),
            ("Nginx", "devops", 80),
            ("Grafana", "devops", 80),
            ("Loki", "devops", 70),
            ("Git/Linux", "devops", 90),
        ]
        for i, (name, cat, prof) in enumerate(techs):
            Technology.objects.update_or_create(
                name=name, defaults={"category": cat, "proficiency": prof, "sort_order": i}
            )

    def _pricing(self):
        plans = [
            {
                "name": "Лендинг",
                "price": 30000,
                "period": "разово",
                "description": "Для запуска продукта или акции",
                "features": ["Продающая структура", "Адаптивный дизайн", "Форма заявки", "Аналитика"],
                "is_popular": False,
                "sort_order": 1,
            },
            {
                "name": "Сайт под ключ",
                "price": 90000,
                "period": "разово",
                "description": "Корпоративный сайт или сервис",
                "features": [
                    "Уникальный дизайн",
                    "Админка контента",
                    "Интеграции",
                    "SEO + аналитика",
                    "Поддержка 1 месяц",
                ],
                "is_popular": True,
                "badge": "Популярный",
                "sort_order": 2,
            },
            {
                "name": "Поддержка",
                "price": 15000,
                "period": "/мес",
                "description": "Постоянное сопровождение проекта",
                "features": ["Исправление ошибок", "Доработки", "Обновления", "Мониторинг"],
                "is_popular": False,
                "sort_order": 3,
            },
        ]
        for data in plans:
            PricingPlan.objects.update_or_create(name=data["name"], defaults=data)

    def _process(self):
        steps = [
            ("Бриф и анализ", "Обсуждаем задачу, цели и метрики. Фиксируем ТЗ и оценку."),
            ("Прототип и дизайн", "Собираю структуру и макет, согласовываем до разработки."),
            ("Разработка", "Работаю спринтами, показываю промежуточные результаты."),
            ("Тестирование и запуск", "Проверяю на реальных данных, деплою и настраиваю мониторинг."),
            ("Поддержка", "Сопровождаю, развиваю и улучшаю продукт после запуска."),
        ]
        for i, (title, desc) in enumerate(steps):
            ProcessStep.objects.update_or_create(title=title, defaults={"description": desc, "sort_order": i})

    def _projects(self):
        tags = {
            "django": "Django",
            "angular": "Angular",
            "fastapi": "FastAPI",
            "telegram": "Telegram-бот",
            "clickhouse": "ClickHouse",
            "integration": "Интеграция",
        }
        tag_objs = {}
        for slug, name in tags.items():
            tag_objs[slug], _ = ProjectTag.objects.update_or_create(slug=slug, defaults={"name": name})

        projects = [
            {
                "title": "Платформа телеметрии ATS",
                "slug": "ats-telemetry",
                "client": "Спутниковое приборостроение",
                "year": 2025,
                "short_description": "Сбор и визуализация CAN-логов испытательных стендов в реальном времени.",
                "description": (
                    "Система принимает CAN-телеметрию со стендов, складывает её через Redis Streams "
                    "в ClickHouse и отдаёт в Grafana. Настроены алерты, сквозная трассировка и дашборды."
                ),
                "tags": ["django", "clickhouse"],
                "stack": ["Python", "Django", "Redis Streams", "ClickHouse", "Grafana"],
                "results": [
                    "Поток до 10k сообщений/сек",
                    "Дашборды в реальном времени",
                    "Сквозная трассировка запросов",
                ],
                "is_featured": True,
            },
            {
                "title": "Система заявок на спутниковую съёмку",
                "slug": "satellite-ordering",
                "client": "Гео-сервис",
                "year": 2024,
                "short_description": "Сервис подачи заявок на спутниковую съёмку с геометрией и датами.",
                "description": (
                    "Django/DRF + PostGIS: пользователи задают полигоны съёмки, сроки и получают "
                    "расчёт. Фоновая обработка на Celery, асинхронные задачи и уведомления."
                ),
                "tags": ["django"],
                "stack": ["Django", "DRF", "PostGIS", "Celery", "Redis"],
                "results": ["Гео-поиск полигонов", "Асинхронная обработка", "Личный кабинет заказчика"],
                "is_featured": True,
            },
            {
                "title": "Телеграм-бот поддержки",
                "slug": "support-bot",
                "client": "Сервисный бизнес",
                "year": 2024,
                "short_description": "Бот-автоответчик с тикетами, оплатой и рассылками.",
                "description": (
                    "Бот принимает обращения, ведёт тикеты в PostgreSQL, умеет принимать платежи "
                    "и делать массовые рассылки. Админ-панель для менеджеров."
                ),
                "tags": ["telegram"],
                "stack": ["Python", "aiogram", "PostgreSQL"],
                "results": ["Автоответы 24/7", "Снижение нагрузки на поддержку", "Приём платежей"],
                "is_featured": False,
            },
            {
                "title": "Корпоративный портал",
                "slug": "corporate-portal",
                "client": "Производственная компания",
                "year": 2023,
                "short_description": "Внутренний портал на Angular + Django API.",
                "description": (
                    "Портал с дашбордами, документами и заявками. SPA на Angular, REST API на "
                    "Django/DRF, ролевая модель доступа."
                ),
                "tags": ["angular", "django"],
                "stack": ["Angular", "Django/DRF", "PostgreSQL"],
                "results": ["Единая точка входа", "Ролевая модель", "Быстрый UI"],
                "is_featured": False,
            },
        ]
        for i, data in enumerate(projects):
            tag_objs_list = [tag_objs[t] for t in data["tags"]]
            data.pop("tags")
            project, _ = Project.objects.update_or_create(slug=data["slug"], defaults={**data, "sort_order": i})
            project.tags.set(tag_objs_list)

    def _skills(self):
        groups = [
            ("Backend", ["Python", "Django", "FastAPI", "Celery", "Go (изучаю)"]),
            ("Frontend", ["Angular", "TypeScript", "JavaScript", "Tailwind CSS"]),
            ("Базы данных", ["PostgreSQL", "ClickHouse", "Redis", "InfluxDB"]),
            ("DevOps", ["Docker", "Nginx", "Grafana", "Loki", "Linux"]),
        ]
        for gi, (name, skill_names) in enumerate(groups):
            group, _ = SkillGroup.objects.update_or_create(name=name, defaults={"sort_order": gi})
            for si, skill_name in enumerate(skill_names):
                Skill.objects.update_or_create(
                    group=group,
                    name=skill_name,
                    defaults={"level": 80 + (si % 3) * 5, "sort_order": si},
                )

    def _testimonials(self):
        data = [
            {
                "author": "Дмитрий",
                "position": "Технический директор",
                "company": "Спутниковое приборостроение",
                "rating": 5,
                "text": (
                    "Собрал нам платформу телеметрии с нуля. Всё работает стабильно, "
                    "код чистый, документация на месте. Рекомендую."
                ),
            },
            {
                "author": "Мария",
                "position": "Product-менеджер",
                "company": "Гео-сервис",
                "rating": 5,
                "text": (
                    "Быстро вник в предметную область, предложил решения, о которых мы не подумали. Сроки соблюдал."
                ),
            },
            {
                "author": "Игорь",
                "position": "Основатель",
                "company": "Сервисный бизнес",
                "rating": 4,
                "text": (
                    "Сделал бота для поддержки — клиенты довольны, нагрузка на менеджеров упала. Отличная коммуникация."
                ),
            },
        ]
        for i, item in enumerate(data):
            Testimonial.objects.update_or_create(author=item["author"], defaults={**item, "sort_order": i})

    def _faq(self):
        cats = {
            "cooperation": "Сотрудничество",
            "payment": "Оплата и сроки",
        }
        cat_objs = {}
        for slug, name in cats.items():
            cat_objs[slug], _ = FAQCategory.objects.update_or_create(slug=slug, defaults={"name": name})

        items = [
            (
                "cooperation",
                "Как начать работу над проектом?",
                "Напишите через форму на сайте или в Telegram — обсудим задачу, "
                "я задам уточняющие вопросы и подготовлю оценку.",
            ),
            (
                "cooperation",
                "Работаете ли вы с NDA?",
                "Да, при необходимости подпишу соглашение о неразглашении до обсуждения деталей.",
            ),
            (
                "cooperation",
                "Как происходит коммуникация?",
                "Основной канал — Telegram, плюс регулярные демо и отчёты о прогрессе.",
            ),
            (
                "payment",
                "Сколько стоит разработка?",
                "Зависит от задачи: лендинг — от 30 000 ₽, сайт под ключ — от 90 000 ₽. Точную оценку дам после брифа.",
            ),
            (
                "payment",
                "Как оплачивать работу?",
                "Обычно 50% предоплата, остальное — по завершении. Для крупных проектов — поэтапная оплата.",
            ),
            (
                "payment",
                "Что входит в поддержку после запуска?",
                "Исправление ошибок, обновления зависимостей, доработки и мониторинг — по договорённости.",
            ),
        ]
        for i, (cat_slug, q, a) in enumerate(items):
            FAQItem.objects.update_or_create(
                category=cat_objs[cat_slug], question=q, defaults={"answer": a, "sort_order": i}
            )

    def _budgets(self):
        labels = ["до 50 000 ₽", "50 000 – 150 000 ₽", "150 000 – 500 000 ₽", "500 000+ ₽", "Пока не знаю"]
        for i, label in enumerate(labels):
            BudgetRange.objects.update_or_create(label=label, defaults={"sort_order": i})

    def _blog(self):
        posts = [
            {
                "title": "Как выбрать стек для стартапа в 2026",
                "slug": "stack-for-startup-2026",
                "excerpt": "Практический разбор: на чём дешевле и быстрее собрать MVP.",
                "content": (
                    "## Введение\n\nВыбор стека определяет скорость и стоимость разработки.\n\n"
                    "Для MVP чаще всего выигрывают связки Django/DRF + PostgreSQL на бэке "
                    "и Angular/React на фронте: зрелая экосистема, быстрая разработка, "
                    "доступные специалисты.\n\n"
                    "## Вывод\n\nНе гонитесь за модными инструментами — выбирайте то, "
                    "что ускоряет доставку ценности."
                ),
                "tags": ["стартап", "django", "angular"],
                "reading_time": 6,
            },
            {
                "title": "ClickHouse для телеметрии: как мы строим хранилище",
                "slug": "clickhouse-telemetry",
                "excerpt": "Поток CAN-логов через Redis Streams в ClickHouse: практика.",
                "content": (
                    "## Задача\n\nПринимать телеметрию испытательных стендов в реальном времени "
                    "и отдавать её в Grafana.\n\n"
                    "## Решение\n\nRedis Streams буферизует поток, ClickHouse хранит и агрегирует, "
                    "Grafana строит дашборды. Сквозной trace_id связывает запросы.\n\n"
                    "Итог — дашборды в реальном времени и алерты."
                ),
                "tags": ["clickhouse", "телеметрия", "grafana"],
                "reading_time": 8,
            },
        ]
        for i, data in enumerate(posts):
            Post.objects.update_or_create(
                slug=data["slug"],
                defaults={**data, "is_published": True, "published_at": timezone.now(), "sort_order": i},
            )
