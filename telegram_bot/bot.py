from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from django.conf import settings

from telegram_bot.handlers.general.start import router as start_router
from telegram_bot.handlers.general.help import router as help_router
from telegram_bot.handlers.general.other import router as other_router
from telegram_bot.handlers.appeals.my_appeals import router as my_appeals_router
from telegram_bot.handlers.commissions.commissions_info import router as commissions_info_router
from telegram_bot.handlers.appeals.write_appeal import router as write_appeal_router
from telegram_bot.handlers.admin_commands.general_admin_commands import router as admin_commands_router
from telegram_bot.handlers.admin_requests.admin_appeal import router as admin_appeal_router
from telegram_bot.handlers.admin_commands.manage_commission import router as manage_commissions_router
from telegram_bot.handlers.admin_commands.manage_admin_requests import router as manage_admin_requests_router
from telegram_bot.handlers.admin_commands.manage_appeals import router as manage_appeals_router
from telegram_bot.handlers.admin_commands.delete_user import router as manage_users_router
from telegram_bot.handlers.general.web_app_enter import router as web_app_enter_router
from .middlewares.auth_middleware import CheckUserRegisteredMiddleware

from .tools.notifier_func import start_notification_task

from .tools.main_logger import logger
from .tools.notifs_deleter_func import start_notification_cleanup_task

# === ХРАНИЛИЩЕ СОСТОЯНИЙ ===
storage = MemoryStorage()  # Инициализация хранилища состояний

# === ИНИЦИАЛИЗАЦИЯ БОТА И ДИСПЕТЧЕРА ===
bot = Bot(token=settings.TELEGRAM_API_TOKEN)
dp = Dispatcher(storage=storage)  # Передаем storage в Dispatcher

# === РЕГИСТРАЦИЯ MIDDLEWARE ===
dp.message.middleware(CheckUserRegisteredMiddleware())

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
dp.include_router(manage_users_router)
dp.include_router(web_app_enter_router)

# === РЕГИСТРАЦИЯ РОУТЕРА ПРОСТО ТЕКСТОВЫХ СООБЩЕНИЙ ===
dp.include_router(other_router)


# === МЕТОД ДЛЯ ЗАПУСКА БОТА ===
async def start_bot():
    """
    Основной метод для запуска бота и фоновых задач.
    """
    try:
        # 1. Сначала сбрасываем все pending updates
        await bot.delete_webhook(drop_pending_updates=True)
        await asyncio.sleep(1)  # Необязательно, но снижает риск пропустить апдейты

        # 2. Запускаем фоновые задачи
        notification_task = asyncio.create_task(start_notification_task(bot))
        cleanup_task = asyncio.create_task(start_notification_cleanup_task())

        try:
            # 3. Запускаем бота с двойной страховкой (webhook + polling)
            await dp.start_polling(bot, skip_updates=True)
        finally:
            # 4. Корректная остановка фоновых задач
            notification_task.cancel()
            cleanup_task.cancel()

            try:
                await notification_task
            except asyncio.CancelledError:
                logger.info("Задача отправки уведомлений отменена.")

            try:
                await cleanup_task
            except asyncio.CancelledError:
                logger.info("Задача очистки уведомлений отменена.")

    except Exception as e:
        logger.error(f"Произошла критическая ошибка при запуске бота: {e}")
        raise