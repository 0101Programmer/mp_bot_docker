
from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import Message

from ...tools.check_is_registred import get_user_by_telegram_id
from ...tools.main_logger import logger
from ...tools.web_app_link_generator import generate_personal_link

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