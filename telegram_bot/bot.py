from aiogram import Bot, Dispatcher
import asyncio
from django.conf import settings
from telegram_bot.handlers.start import router as start_router
from telegram_bot.handlers.help import router as help_router
from telegram_bot.handlers.other import router as other_router

# Инициализация бота и диспетчера
bot = Bot(token=settings.TELEGRAM_API_TOKEN)
dp = Dispatcher()

# Регистрация роутеров
dp.include_router(start_router)
dp.include_router(help_router)
dp.include_router(other_router)


# Функция для отправки уведомлений (фоновая задача)
async def send_notifications():
    while True:
        print("Отправка уведомлений...")
        await asyncio.sleep(60)  # Отправляем каждые 60 секунд


# Метод для запуска бота
async def start_bot():
    # Создаем задачу для отправки уведомлений
    notification_task = asyncio.create_task(send_notifications())

    try:
        # Запускаем бота
        await dp.start_polling(bot, skip_updates=True)
    finally:
        # Отменяем задачу отправки уведомлений при завершении работы бота
        notification_task.cancel()
        try:
            await notification_task
        except asyncio.CancelledError:
            print("Задача отправки уведомлений отменена.")