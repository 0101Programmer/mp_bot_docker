import asyncio
from django.core.management.base import BaseCommand
from telegram_bot.old_bot import dp, bot, send_notifications


class Command(BaseCommand):
    help = 'Запуск Telegram-бота (aiogram 3.x)'

    async def main(self):
        # Создаем задачу для отправки уведомлений
        notification_task = asyncio.create_task(send_notifications())

        # Запускаем бота
        await dp.start_polling(bot, skip_updates=True)

        # Дожидаемся завершения задачи отправки уведомлений
        await notification_task

    def handle(self, *args, **options):
        # Запускаем асинхронную функцию main через asyncio.run
        asyncio.run(self.main())