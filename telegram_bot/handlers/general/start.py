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
    user_data = {
        "telegram_id": message.from_user.id,
        "username": message.from_user.username or "",
        "first_name": message.from_user.first_name or "",
        "last_name": message.from_user.last_name or "",
    }

    await sync_to_async(User.objects.update_or_create)(
        telegram_id=user_data["telegram_id"],
        defaults=user_data
    )

    await message.answer(
        "Привет! Добро пожаловать в чат-бот молодежного парламента.\n"
        "Пожалуйста, выберите действие",
        reply_markup=start_keyboard
    )