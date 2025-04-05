from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ...tools.check_admin_requests import check_admin_requests
from ...tools.check_is_registred import get_user_by_telegram_id

# Создаем роутер для обработки команд
router = Router()

def get_admin_main_menu_keyboard():
    """Создает клавиатуру для главного меню администратора."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Заявки на получение администратора", callback_data="admin_requests")
    builder.button(text="Действия с комиссиями", callback_data="commission_actions")
    builder.button(text="Просмотр обращений", callback_data="view_appeals")
    builder.button(text="Действия с пользователями", callback_data="user_actions")
    builder.adjust(1)
    return builder.as_markup()

# Команда /admin
@router.message(Command("admin"))
async def admin_command(message: Message):
    # Получаем Telegram ID пользователя
    telegram_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    user = await get_user_by_telegram_id(telegram_id)
    if not user:
        await message.answer("Вы не зарегистрированы. Пожалуйста, начните с команды /start.")
        return

    # Проверяем, является ли пользователь администратором
    if user.is_admin:
        # Отправляем главное меню администратора
        await message.answer("Выберите категорию:", reply_markup=get_admin_main_menu_keyboard())
    else:
        # Проверяем статус заявок пользователя
        response, reply_markup = await check_admin_requests(user)
        await message.answer(response, reply_markup=reply_markup)



# Обработчик для кнопки "Назад"
@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    # Редактируем сообщение, чтобы вернуться к начальному меню
    await callback.message.edit_text("Выберите категорию:", reply_markup=get_admin_main_menu_keyboard())