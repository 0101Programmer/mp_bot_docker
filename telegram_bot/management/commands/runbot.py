import asyncio
from django.core.management.base import BaseCommand
from aiogram.utils import executor
from telegram_bot.bot import dp, send_notifications

class Command(BaseCommand):
    help = 'Запуск Telegram-бота (aiogram)'

    def handle(self, *args, **options):
        loop = asyncio.get_event_loop()
        loop.create_task(send_notifications())
        executor.start_polling(dp, skip_updates=True)