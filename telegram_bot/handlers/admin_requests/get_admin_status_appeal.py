from typing import Dict, Any

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from asgiref.sync import sync_to_async

from ...models import AdminRequest, User
from ...tools.check_admin_requests import check_admin_requests
from ...tools.main_logger import logger

# Создаем роутер для обработки команд
router = Router()

# Определяем состояния
class AdminRequestState(StatesGroup):
    waiting_for_position = State()  # Состояние для ожидания ввода должности


# Обработчик нажатия на кнопку "Подать заявку"
@router.callback_query(F.data == "submit_admin_request")
async def submit_admin_request(
        callback: CallbackQuery,
        state: FSMContext,
        user: User
):
    """Обработчик подачи заявки с получением данных из middleware"""

    # Получаем данные из состояния (куда middleware их сохранил)
    state_data = await state.get_data()
    request_data = state_data.get('admin_request', {})

    allow_submit = request_data.get('allow_submit', False)
    response = request_data.get('response', '')

    if not allow_submit:
        await callback.answer(response, show_alert=True)
        return

    # Удаляем кнопку
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except:
        pass

    await callback.message.answer(
        "Введите вашу должность для получения административных прав.\n"
        "Пример: «Модератор сообщества» или «Технический администратор»"
    )

    await state.update_data(user_id=user.id)
    await state.set_state(AdminRequestState.waiting_for_position)
    await callback.answer()


# Обработчик ввода должности
@router.message(StateFilter(AdminRequestState.waiting_for_position))
async def process_position(message: Message, state: FSMContext):
    # Получаем Telegram ID пользователя
    telegram_id = message.from_user.id

    try:
        # Находим пользователя в базе данных
        user = await sync_to_async(User.objects.get)(telegram_id=telegram_id)

        # Проверяем, есть ли у пользователя отклонённые заявки
        rejected_requests_exist = await sync_to_async(
            AdminRequest.objects.filter(user=user, status='rejected').exists
        )()
        if rejected_requests_exist:
            # Удаляем все отклонённые заявки
            await sync_to_async(AdminRequest.objects.filter(user=user, status='rejected').delete)()
            logger.info("Старые отклонённые заявки пользователя были удалены.")

        # Создаем новую заявку
        await sync_to_async(AdminRequest.objects.create)(
            user=user,
            admin_position=message.text
        )

        # Отправляем подтверждение
        await message.answer(
            f"Ваша заявка на должность '{message.text}' успешно отправлена. Ожидайте одобрения."
        )

        # Сбрасываем состояние
        await state.clear()

    except User.DoesNotExist:
        await message.answer("Произошла ошибка. Пожалуйста, начните с команды /start.")