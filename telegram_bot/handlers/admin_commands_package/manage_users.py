from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from ...models import User, AdminRequest
from django.db.utils import IntegrityError

router = Router()


# Состояния для FSM
class UserAction(StatesGroup):
    waiting_for_user_id = State()
    editing_field = State()


# Обработчик для входа в меню действий с пользователями
@router.callback_query(F.data == "user_actions")
async def user_actions_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Введите ID пользователя:")
    await state.set_state(UserAction.waiting_for_user_id)


# Обработчик ввода ID пользователя
@router.message(UserAction.waiting_for_user_id)
async def process_user_id(message: Message, state: FSMContext):
    user_id = message.text.strip()

    # Проверяем, что введено число
    if not user_id.isdigit():
        await message.answer("ID должно быть числом. Попробуйте снова.")
        return

    user_id = int(user_id)

    # Получаем пользователя из базы данных
    user = await sync_to_async(User.objects.filter(user_id=user_id).first)()

    if not user:
        await message.answer("Пользователь с таким ID не найден. Попробуйте снова.")
        await state.clear()  # Завершаем состояние, если пользователь не найден
        return

    # Сохраняем ID пользователя в состояние
    await state.update_data(selected_user_id=user.user_id)

    # Формируем сообщение с данными пользователя
    user_info = (
        f"Информация о пользователе:\n"
        f"ID: {user.user_id}\n"
        f"Telegram ID: {user.telegram_id}\n"
        f"Username: {user.username}\n"
        f"Имя: {user.first_name}\n"
        f"Фамилия: {user.last_name}\n"
        f"Админ: {'Да' if user.is_admin else 'Нет'}"
    )

    # Создаем клавиатуру с кнопками
    builder = InlineKeyboardBuilder()

    # Кнопки для редактирования полей
    builder.add(InlineKeyboardButton(text="Редактировать имя", callback_data=f"edit_first_name"))
    builder.add(InlineKeyboardButton(text="Редактировать фамилию", callback_data=f"edit_last_name"))

    # Кнопка для изменения статуса админа (если это не текущий пользователь)
    current_user_id = message.from_user.id  # Telegram ID текущего пользователя
    if user.telegram_id != current_user_id and user.is_admin:
        builder.add(InlineKeyboardButton(text="Снять статус администратора", callback_data=f"remove_admin"))

    # Кнопка для удаления пользователя (если это не текущий пользователь)
    if user.telegram_id != current_user_id:
        builder.add(InlineKeyboardButton(text="Удалить пользователя", callback_data=f"delete_user"))

    # Устанавливаем кнопки друг под другом
    builder.adjust(1)

    # Отправляем сообщение с данными пользователя и кнопками
    await message.answer(user_info, reply_markup=builder.as_markup())

    # Переходим в состояние ожидания выбора действия
    await state.set_state(UserAction.editing_field)


# Обработчик нажатий на кнопки
@router.callback_query(UserAction.editing_field)
async def process_action(callback: CallbackQuery, state: FSMContext):
    action = callback.data
    data = await state.get_data()
    user_id = data.get("selected_user_id")

    # Получаем пользователя из базы данных
    user = await sync_to_async(User.objects.filter(user_id=user_id).first)()

    if not user:
        await callback.message.answer("Пользователь не найден. Попробуйте снова.")
        await state.clear()  # Завершаем состояние, если пользователь не найден
        return

    try:
        if action == "edit_first_name":
            await callback.message.answer("Введите новое имя:")
            await state.update_data(editing_field="first_name")
        elif action == "edit_last_name":
            await callback.message.answer("Введите новую фамилию:")
            await state.update_data(editing_field="last_name")
        elif action == "remove_admin":
            # Снимаем статус админа
            user.is_admin = False

            # Проверяем таблицу AdminRequest на наличие записи со статусом 'approved'
            admin_request = await sync_to_async(AdminRequest.objects.filter(user=user, status='approved').first)()

            if admin_request:
                # Обновляем статус и добавляем комментарий
                admin_request.status = 'rejected'
                admin_request.comment = "Статус отозван"
                await sync_to_async(admin_request.save)()

            # Сохраняем изменения пользователя
            await sync_to_async(user.save)()

            # Отправляем уведомление
            await callback.message.edit_text(
                "Статус админа успешно снят. Все связанные запросы на админку обновлены.",
                reply_markup=None  # Убираем клавиатуру
            )
        elif action == "delete_user":
            await sync_to_async(user.delete)()
            await callback.message.edit_text(
                "Пользователь успешно удален.",
                reply_markup=None  # Убираем клавиатуру
            )
            await state.clear()  # Завершаем состояние после удаления
            return

        await callback.answer()

    except IntegrityError as e:
        # Логируем ошибку
        print(f"Database IntegrityError: {e}")

        # Отправляем сообщение пользователю
        await callback.message.answer("Что-то пошло не так, но мы уже работаем над этим!")

        # Убираем клавиатуру, чтобы кнопка не "зависала"
        await callback.message.edit_reply_markup(reply_markup=None)


# Обработчик ввода нового значения для поля
@router.message(UserAction.editing_field)
async def process_edit_field(message: Message, state: FSMContext):
    new_value = message.text.strip()
    data = await state.get_data()
    field = data.get("editing_field")
    user_id = data.get("selected_user_id")

    # Проверяем, что есть поле для редактирования и ID пользователя
    if not field or not user_id:
        await message.answer("Произошла ошибка. Пожалуйста, начните сначала.")
        await state.clear()  # Завершаем состояние
        return

    # Получаем пользователя из базы данных
    user = await sync_to_async(User.objects.filter(user_id=user_id).first)()

    if not user:
        await message.answer("Пользователь не найден. Попробуйте снова.")
        await state.clear()  # Завершаем состояние
        return

    # Обновляем поле
    if field == "first_name":
        user.first_name = new_value
    elif field == "last_name":
        user.last_name = new_value
    else:
        await message.answer("Некорректное поле для редактирования. Пожалуйста, начните сначала.")
        await state.clear()  # Завершаем состояние
        return

    await sync_to_async(user.save)()

    # Отправляем уведомление об успешном обновлении
    await message.answer(f"Поле '{field}' успешно обновлено.")

    # Очищаем состояние
    await state.clear()