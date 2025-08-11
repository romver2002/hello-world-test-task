import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

celery_app = Celery(
    "hero_tasks",
    broker=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
    include=["app.tasks.post_hero"],  # гарантированная регистрация задач
)
celery_app.conf.timezone = os.getenv("TIMEZONE", "UTC")

# Явно импортируем модуль задач, чтобы воркер их зарегистрировал
celery_app.autodiscover_tasks(["app"])  # найдёт пакет app.tasks
try:
    from app.tasks import post_hero  # noqa: F401
except Exception:
    # при импорте на этапе сборки контейнера задач может не быть — не критично
    pass

# Интервальное расписание (каждые N минут), если указано
POST_EVERY_MINUTES = os.getenv("POST_EVERY_MINUTES")
if POST_EVERY_MINUTES:
    try:
        minutes = int(POST_EVERY_MINUTES)
        celery_app.conf.beat_schedule = getattr(celery_app.conf, "beat_schedule", {}) | {
            "post-all-heroes-interval": {
                "task": "app.tasks.post_hero.post_all_heroes",
                "schedule": timedelta(minutes=minutes),
            }
        }
    except ValueError:
        pass

# Опциональное расписание через CRON, если переменная установлена
POST_CRON = os.getenv("POST_CRON")  # пример: "0 9 * * *"
if POST_CRON:
    minute, hour, day_of_month, month, day_of_week = POST_CRON.split()
    celery_app.conf.beat_schedule = getattr(celery_app.conf, "beat_schedule", {}) | {
        "post-hero-by-cron": {
            "task": "app.tasks.post_hero.post_all_heroes",
            "schedule": crontab(
                minute=minute,
                hour=hour,
                day_of_month=day_of_month,
                month_of_year=month,
                day_of_week=day_of_week,
            ),
        }
    }


