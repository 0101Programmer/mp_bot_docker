from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.contrib.auth import get_user_model
from django.conf import settings
from .tools.main_logger import logger


def create_superuser(sender, **kwargs):
    """
    Функция для создания суперпользователя после применения миграций.
    """
    User = get_user_model()
    if not User.objects.filter(is_superuser=True).exists():
        try:
            User.objects.create_superuser(
                username=settings.DJANGO_SUPERUSER_NAME,
                password=settings.DJANGO_SUPERUSER_PASSWORD,
                email=''  # Можно указать email, если требуется
            )
            logger.info("Superuser created successfully.")
        except Exception as e:
            logger.error(f"An error occurred while creating superuser: {e}")
    else:
        logger.info("Superuser already exists.")


class TelegramBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bot'

    def ready(self):
        # Импорт сигналов
        try:
            import telegram_bot.signals
            logger.info("Сигналы успешно импортированы.")
        except ImportError as e:
            logger.error(f"Ошибка при импорте сигналов: {e}")

        # Подключаем сигнал post_migrate для создания суперпользователя
        post_migrate.connect(create_superuser, sender=self)