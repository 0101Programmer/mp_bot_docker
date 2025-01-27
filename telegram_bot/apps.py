from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class TelegramBotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bot'

    def ready(self):
            import telegram_bot.signals  # Подключение signals.py
            logger.info("Сигналы успешно импортированы.")