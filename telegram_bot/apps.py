from django.apps import AppConfig
from .tools.main_logger import logger


class TelegramBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bot'

    def ready(self):
            import telegram_bot.signals  # Подключение signals.py
            logger.info("Сигналы успешно импортированы.")