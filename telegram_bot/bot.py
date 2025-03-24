from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import logging
from django.conf import settings

from telegram_bot.handlers import admin_commands_package
from telegram_bot.handlers.start import router as start_router
from telegram_bot.handlers.help import router as help_router
from telegram_bot.handlers.other import router as other_router
from telegram_bot.handlers.my_appeals import router as my_appeals_router
from telegram_bot.handlers.commissions_info import router as commissions_info_router
from telegram_bot.handlers.write_appeal import router as write_appeal_router
from telegram_bot.handlers.admin_commands import router as admin_commands_router
from telegram_bot.handlers.admin_appeal import router as admin_appeal_router
from telegram_bot.handlers.admin_commands_package.manage_commission import router as manage_commissions_router
from telegram_bot.handlers.admin_commands_package.manage_admin_requests import router as manage_admin_requests_router
from telegram_bot.handlers.admin_commands_package.manage_appeals import router as manage_appeals_router




# === ЛОГИРОВАНИЕ ===
logging.basicConfig(
    level=logging.INFO,  # Уровень логов (INFO - информационные сообщения)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Формат логов
)
logger = logging.getLogger(__name__)  # Создаем экземпляр логгера

# === ХРАНИЛИЩЕ СОСТОЯНИЙ ===
storage = MemoryStorage()  # Инициализация хранилища состояний

# === ИНИЦИАЛИЗАЦИЯ БОТА И ДИСПЕТЧЕРА ===
bot = Bot(token=settings.TELEGRAM_API_TOKEN)
dp = Dispatcher(storage=storage)  # Передаем storage в Dispatcher

# === РЕГИСТРАЦИЯ РОУТЕРОВ ===
dp.include_router(start_router)
dp.include_router(help_router)
dp.include_router(my_appeals_router)
dp.include_router(commissions_info_router)
dp.include_router(write_appeal_router)
dp.include_router(admin_commands_router)
dp.include_router(admin_appeal_router)
dp.include_router(manage_commissions_router)
dp.include_router(manage_admin_requests_router)
dp.include_router(manage_appeals_router)

# === РЕГИСТРАЦИЯ РОУТЕРА ПРОСТО ТЕКСТОВЫХ СООБЩЕНИЙ ===
dp.include_router(other_router)

# === ФОНОВАЯ ЗАДАЧА ===
async def send_notifications():
    while True:
        logger.info("Отправка уведомлений...")  # Логируем отправку уведомлений
        await asyncio.sleep(60)  # Отправляем каждые 60 секунд

# === МЕТОД ДЛЯ ЗАПУСКА БОТА ===
async def start_bot():
    logger.info("Запуск бота...")  # Логируем запуск бота
    notification_task = asyncio.create_task(send_notifications())  # Создаем фоновую задачу

    try:
        await dp.start_polling(bot, skip_updates=True)  # Запускаем бота
    finally:
        notification_task.cancel()  # Отменяем задачу при завершении работы бота
        try:
            await notification_task
        except asyncio.CancelledError:
            logger.info("Задача отправки уведомлений отменена.")  # Логируем отмену задачи