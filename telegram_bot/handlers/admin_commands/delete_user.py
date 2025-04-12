from aiogram import Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ...models import User

# Создаем роутер
router = Router()

# Определяем состояния для FSM
class DeleteUserStates(StatesGroup):
    waiting_for_user_id = State()  # Ожидание ввода ID пользователя

# Функция для создания клавиатуры с кнопкой "Отменить поиск"
def get_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Отменить поиск", callback_data="cancel_search")
    builder.adjust(1)
    return builder.as_markup()

# Обработчик для команды /delete_user или кнопки "Удалить пользователя"
@router.callback_query(F.data == "delete_user")
async def request_user_id(callback: CallbackQuery, state: FSMContext):
    # Отправляем сообщение с запросом ID и кнопкой "Отменить поиск"
    await callback.message.answer(
        "Введите ID пользователя (primary key), которого хотите удалить:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(DeleteUserStates.waiting_for_user_id)

    # Подтверждаем обработку callback-запроса
    await callback.answer()

# Обработчик для ввода ID пользователя
@router.message(DeleteUserStates.waiting_for_user_id)
async def process_user_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)  # Преобразуем введенный текст в число
    except ValueError:
        await message.answer(
            "ID пользователя должен быть числом. Попробуйте снова.",
            reply_markup=get_cancel_keyboard()
        )
        return

    # Асинхронный запрос к базе данных
    user = await sync_to_async(User.objects.filter(id=user_id).first)()
    if not user:
        await message.answer(
            "Пользователь с таким ID не найден. Попробуйте снова.",
            reply_markup=get_cancel_keyboard()
        )
        return

    # Создаем клавиатуру с кнопкой "Удалить"
    builder = InlineKeyboardBuilder()
    builder.button(text="Удалить", callback_data=f"confirm_delete_{user.id}")
    builder.adjust(1)

    # Отправляем карточку пользователя
    user_card = (
        f"Пользователь:\n"
        f"ID (PK): {user.id}\n"
        f"Telegram ID: {user.telegram_id}\n"
        f"Имя: {user.first_name}\n"
        f"Фамилия: {user.last_name}\n"
        f"Username: @{user.username}\n"
        f"Администратор: {'Да' if user.is_admin else 'Нет'}\n"
        f"Дата создания: {user.created_at.strftime('%d.%m.%Y %H:%M')}"
    )
    await message.answer(user_card, reply_markup=builder.as_markup())

    # Сбрасываем состояние
    await state.clear()

# Обработчик подтверждения удаления
@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_user(callback: CallbackQuery):
    user_id = int(callback.data.split("_")[-1])  # Извлекаем ID пользователя из callback_data

    # Асинхронный запрос к базе данных
    user = await sync_to_async(User.objects.filter(id=user_id).first)()
    if user:
        await sync_to_async(user.delete)()
        await callback.message.answer(f"Пользователь с ID (PK) {user_id} успешно удален.")
    else:
        await callback.message.answer("Пользователь не найден.")

    # Удаляем inline-клавиатуру после выполнения действия
    await callback.message.edit_reply_markup(reply_markup=None)

    # Подтверждаем обработку callback-запроса
    await callback.answer()

# Обработчик кнопки "Отменить поиск"
@router.callback_query(F.data == "cancel_search")
async def cancel_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Поиск отменен.")
    await state.clear()  # Сбрасываем состояние

    # Удаляем inline-клавиатуру из текущего сообщения
    await callback.message.edit_reply_markup(reply_markup=None)

    # Подтверждаем обработку callback-запроса
    await callback.answer()