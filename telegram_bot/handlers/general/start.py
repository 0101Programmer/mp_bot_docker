from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram import Router
from asgiref.sync import sync_to_async

# Импорт Django-моделей
from ...models import User, Appeal, CommissionInfo, Notification, AdminRequest

from ...keyboards.start_kb import start_keyboard

# Инициализация роутера
router = Router()

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    # Получаем данные пользователя
    telegram_id = message.from_user.id  # Telegram ID пользователя
    username = message.from_user.username or "N/A"  # Если username отсутствует, используем "N/A"
    first_name = message.from_user.first_name or "N/A"  # Если first_name отсутствует, используем "N/A"
    last_name = message.from_user.last_name or "N/A"  # Если last_name отсутствует, используем "N/A"

    # Асинхронная версия get_or_create
    user, created = await sync_to_async(User.objects.get_or_create)(
        telegram_id=telegram_id,
        defaults={
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "is_admin": False,
        }
    )

    if not created:
        # Если пользователь уже существует, обновляем его данные
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        await sync_to_async(user.save)()  # Асинхронное сохранение

    await message.answer("Привет! Добро пожаловать в чат-бот молодежного парламента.\n"
                         "Пожалуйста, выберите действие",
                         reply_markup=start_keyboard)