# Personal Site — Backend

Продающий персональный сайт разработчика. Бэкенд на **Django 6 + Django REST
Framework**, весь контент редактируется через админку и хранится в БД.

## Стек

- **Python 3.14**, **Django 6.1**, **DRF 3.18**
- PostgreSQL (продакшен) / SQLite (дев), управление через `DATABASE_URL`
- drf-spectacular (OpenAPI + Swagger UI), django-filter, whitenoise, gunicorn
- ruff + pytest (качество и тесты)

## Быстрый старт (uv)

```bash
# 1. Установить зависимости (создаст .venv с Python 3.14)
uv sync

# 2. Миграции и демо-контент
uv run python manage.py migrate
uv run python manage.py seed_demo

# 3. Суперпользователь (для админки)
uv run python manage.py createsuperuser

# 4. Запуск
uv run python manage.py runserver
```

Открыть: админка `http://localhost:8000/admin/`, Swagger `http://localhost:8000/api/docs/`.

## Конфигурация

Все настройки — через переменные окружения (см. `.env.example`, скопируй в `.env`).

| Переменная | Назначение | По умолчанию |
|---|---|---|
| `DEBUG` | Режим отладки | `False` |
| `SECRET_KEY` | Секретный ключ | dev-ключ |
| `DATABASE_URL` | Строка подключения БД | `sqlite:///db.sqlite3` |
| `CORS_ALLOWED_ORIGINS` | Разрешённые origin фронта (через запятую) | `http://localhost:4200` |
| `LEAD_NOTIFY_EMAIL` | Email для уведомлений о заявках | пусто (нет уведомлений) |
| `CACHE_URL` | Кэш (опц., Redis) | locmem |

Пример PostgreSQL: `postgres://user:pass@host:5432/site`.

## API

Все ответы — JSON, версионирование через `/api/v1/`.

**Контент (GET):**

| Endpoint | Что отдаёт |
|---|---|
| `/api/v1/site/` | Настройки, hero, about, статистика, соцсети |
| `/api/v1/services/` | Услуги (фильтры: `category__slug`, `is_featured`) |
| `/api/v1/services/categories/` | Категории услуг |
| `/api/v1/services/<slug>/` | Одна услуга |
| `/api/v1/technologies/` · `/pricing/` · `/process/` | Стек, тарифы, этапы |
| `/api/v1/projects/` | Проекты (фильтр: `tags__slug`, `is_featured`) |
| `/api/v1/testimonials/` · `/skills/` · `/faq/` · `/blog/` | Отзывы, навыки, FAQ, блог |
| `/api/v1/requests/budgets/` | Диапазоны бюджета |

**Заявки (POST):**

| Endpoint | Форма |
|---|---|
| `/api/v1/requests/contact/` | Обратная связь |
| `/api/v1/requests/callback/` | Заказать звонок |
| `/api/v1/requests/order/` | Заказ услуги |
| `/api/v1/requests/brief/` | Заявка на разработку (бриф) |
| `/api/v1/requests/consultation/` | Консультация |
| `/api/v1/requests/subscribe/` | Подписка на рассылку |

Тип заявки проставляется сервером — клиент не может его подменить. Все заявки
видны в админке (`Заявки`), статусы и обработка — там же.

## Структура

```
config/           настройки и корневые URL
common/           общие абстрактные модели и валидаторы
core/             настройки сайта, hero, about, статистика, соцсети, seed
services/         услуги, категории, технологии, тарифы, этапы
projects/         портфолио (теги, галереи)
leads/            заявки всех типов
testimonials/     отзывы
skills/           навыки по группам
blog/             посты
faq/              вопросы-ответы
```

## Тесты и качество

```bash
uv run pytest            # тесты
uv run ruff check .      # линт
uv run ruff format .     # форматирование
```

## Продакшен

См. `Dockerfile` (gunicorn + whitenoise) и `docker-compose.yml` (postgres + backend).

```bash
docker compose up -d --build
```

Медиафайлы (`MEDIA_ROOT`) в проде раздаёт nginx (или любой CDN/S3), статику —
whitenoise. SSL обычно терминируется на прокси (`SECURE_SSL_REDIRECT=False`),
включай его в `.env`, только если Django отдаёт HTTPS напрямую.
