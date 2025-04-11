import asyncio
from django.core.management.base import BaseCommand
from telegram_bot.bot import start_bot

class Command(BaseCommand):
    help = 'Запуск Telegram-бота (aiogram 3.x)'

    def handle(self, *args, **options):
        try:
            # Запускаем бота через asyncio.run
            asyncio.run(start_bot())
        except KeyboardInterrupt:
            self.stdout.write("Бот остановлен.")