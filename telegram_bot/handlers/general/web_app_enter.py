from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message

from ...tools.main_logger import logger
from ...tools.web_app_link_generator import generate_personal_link

router = Router()


@router.message(Command("account"))
async def cmd_account(message: Message, user=None):
    """
    Обрабатывает команду /account и отправляет кнопку с персональной ссылкой на личный кабинет.
    :param user: Пользователь, полученный из middleware
    """
    try:
        # Генерируем персональную ссылку
        personal_link = generate_personal_link(user.telegram_id)

        # Создаём кнопку с эмодзи
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🌟 Открыть личный кабинет ✨", url=personal_link)
                ]
            ]
        )

        # Отправляем сообщение с кнопкой и стилизованным текстом
        await message.answer(
            "✨ <b>Добро пожаловать!</b> ✨\n\n"
            "Нажмите на кнопку ниже, чтобы перейти в ваш <b>личный кабинет</b>:",
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    except Exception as e:
        # Логируем ошибку
        logger.error(f"Ошибка при выполнении команды /account: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")