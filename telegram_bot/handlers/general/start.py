from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message
from asgiref.sync import sync_to_async

from ...keyboards.start_kb import start_keyboard
from ...models import User

# Инициализация роутера
router = Router()

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обрабатывает команду /start:
    - Создает или обновляет пользователя в базе данных.
    - Отправляет приветственное сообщение с клавиатурой.
    """
    # Подготовка данных пользователя
    user_data = {
        "telegram_id": message.from_user.id,
        "username": message.from_user.username or "",
        "first_name": message.from_user.first_name or "",
        "last_name": message.from_user.last_name or "",
    }

    # Создание или обновление пользователя в базе данных
    await sync_to_async(User.objects.update_or_create)(
        telegram_id=user_data["telegram_id"],
        defaults=user_data
    )

    # Отправка приветственного сообщения
    await message.answer(
        "Привет! Добро пожаловать в чат-бот молодежного парламента.\n"
        "Пожалуйста, выберите действие:",
        reply_markup=start_keyboard
    )