from django.core.management.base import BaseCommand
from telegram_bot.bot import start_bot_polling

class Command(BaseCommand):
    help = 'Запуск Telegram-бота (aiogram)'

    def handle(self, *args, **options):
        self.stdout.write("Starting Telegram Bot...")
        start_bot_polling()