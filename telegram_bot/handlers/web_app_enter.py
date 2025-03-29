# bot_handlers.py
import logging

from aiogram import Router, F
from aiogram.types import Message
from ..models import User
from ..tools.secret_token_generator import generate_token
from aiogram.filters.command import Command
from asgiref.sync import sync_to_async
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("account"))
async def cmd_account(message: Message):
    """
    Обрабатывает команду /account и отправляет кнопку с персональной ссылкой на личный кабинет.
    """
    telegram_id = message.from_user.id

    try:
        # Находим пользователя в базе данных
        user = await sync_to_async(User.objects.get)(telegram_id=telegram_id)

        # Генерируем токен
        token = generate_token(telegram_id)

        # Формируем персональную ссылку
        personal_link = f"http://127.0.0.1:8000/telegram_bot/frontend_redirect_url/{token}"

        # Логируем ссылку для отладки
        logger.info(f"Generated personal link: {personal_link}")

        # Создаём кнопку
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Перейти в личный кабинет", url=personal_link)
                ]
            ]
        )

        # Отправляем сообщение с кнопкой
        await message.answer(
            "Нажмите на кнопку ниже, чтобы перейти в личный кабинет:",
            reply_markup=keyboard
        )

    except User.DoesNotExist:
        await message.answer("Произошла ошибка. Пожалуйста, начните с команды /start.")