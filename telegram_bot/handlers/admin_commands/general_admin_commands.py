from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Создаем роутер для обработки админ-команд
router = Router()

def get_admin_main_menu_keyboard():
    """Создает клавиатуру для главного меню администратора."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Заявки на получение администратора", callback_data="admin_requests")
    builder.button(text="Действия с комиссиями", callback_data="commission_actions")
    builder.button(text="Просмотр обращений", callback_data="view_appeals")
    builder.button(text="Удалить пользователя", callback_data="delete_user")
    builder.adjust(1)
    return builder.as_markup()

# Команда /admin
@router.message(Command("admin"))
async def admin_command(message: Message):
    """
    Команда /admin.
    Доступна только администраторам (проверка выполняется в мидлвейре).
    """
    await message.answer("Выберите категорию:", reply_markup=get_admin_main_menu_keyboard())

# Обработчик для кнопки "Назад"
@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    # Редактируем сообщение, чтобы вернуться к начальному меню
    await callback.message.edit_text("Выберите категорию:", reply_markup=get_admin_main_menu_keyboard())