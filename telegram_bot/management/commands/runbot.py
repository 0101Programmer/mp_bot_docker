import asyncio
from django.core.management.base import BaseCommand
from django_redis import get_redis_connection
from decouple import config
from telegram_bot.bot import start_bot

USE_DOCKER = config("USE_DOCKER")

class Command(BaseCommand):
    help = 'Запуск Telegram-бота'

    def check_redis(self):
        """
        Проверяет доступность Redis.
        В случае ошибки выводит сообщение и завершает выполнение команды.
        """
        try:
            # Попытка подключиться к Redis
            redis = get_redis_connection("default")
            redis.ping()  # Отправляем PING-запрос
            self.stdout.write(self.style.SUCCESS("Redis is available."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Redis is not available: {e}"))
            self.stderr.write("Stopping bot startup.")
            exit(1)  # Прерываем выполнение

    def handle(self, *args, **options):

        # Проверяем Redis только если USE_DOCKER == "0"
        if USE_DOCKER == "0":
            self.check_redis()

        try:
            # Запускаем бота через asyncio.run
            asyncio.run(start_bot())
        except KeyboardInterrupt:
            self.stdout.write("Бот остановлен.")