from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from ...tools.main_logger import logger
from ...tools.web_app_link_generator import generate_personal_link

router = Router()



# @router.message(Command("account"))
# async def cmd_account(message: Message, user=None):
#     """
#     Обрабатывает команду /account и отправляет кнопку с персональной ссылкой на личный кабинет.
#     :param user: Пользователь, полученный из middleware
#     """
#     try:
#         # Генерируем персональную ссылку
#         web_app_url = generate_personal_link(user.telegram_id)
#
#         # Создаем кнопку Web App
#         keyboard = InlineKeyboardMarkup(
#             inline_keyboard=[
#                 [InlineKeyboardButton(text="🌟 Открыть личный кабинет ✨", web_app=WebAppInfo(url=web_app_url))]
#             ],
#             resize_keyboard=True
#         )
#
#         await message.answer(
#             "✨ <b>Добро пожаловать!</b> ✨\n\n"
#             "Нажмите на кнопку ниже, чтобы открыть личный кабинет:",
#             reply_markup=keyboard,
#             parse_mode='HTML'
#         )
#
#     except Exception as e:
#         logger.error(f"Ошибка в /account: {e}")
#         await message.answer("Произошла ошибка. Попробуйте позже.")

@router.message(Command("account"))
async def cmd_account(message: Message, user=None):
    """
    Обрабатывает команду /account и отправляет кнопку со ссылкой на личный кабинет.
    :param user: Пользователь, полученный из middleware
    """
    try:
        # Генерируем ссылку на WebApp
        web_app_url = generate_personal_link()

        # Создаем кнопку Web App
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="🌟 Открыть личный кабинет ✨", web_app=WebAppInfo(url=web_app_url)
                )]
            ],
            resize_keyboard=True
        )

        await message.answer(
            "✨ <b>Добро пожаловать!</b> ✨\n\n"
            "Нажмите на кнопку ниже, чтобы открыть личный кабинет:",
            reply_markup=keyboard,
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Ошибка в /account: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")