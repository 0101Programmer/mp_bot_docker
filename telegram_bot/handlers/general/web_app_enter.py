import logging

from aiogram import Router, F
from aiogram.types import Message
from ...models import User
from ...tools.check_is_registred import get_user_by_telegram_id
from ...tools.secret_token_generator import generate_token
from aiogram.filters.command import Command
from asgiref.sync import sync_to_async
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ...tools.web_app_link_generator import generate_personal_link

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("account"))
async def cmd_account(message: Message):
    """
    Обрабатывает команду /account и отправляет кнопку с персональной ссылкой на личный кабинет.
    """
    # Получаем Telegram ID пользователя
    telegram_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        await message.answer("Вы не зарегистрированы. Пожалуйста, начните с команды /start.")
        return

    try:
        # Генерируем персональную ссылку
        personal_link = generate_personal_link(telegram_id)

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

    except Exception as e:
        # Логируем ошибку
        logger.error(f"Ошибка при выполнении команды /account: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")