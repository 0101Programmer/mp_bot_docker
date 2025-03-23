from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from asgiref.sync import sync_to_async
from ..models import AdminRequest, User

# Создаем роутер для обработки команд
router = Router()

# Определяем состояния
class AdminRequestState(StatesGroup):
    waiting_for_position = State()  # Состояние для ожидания ввода должности

# Обработчик нажатия на кнопку "Подать заявку"
@router.callback_query(F.data == "submit_admin_request")
async def submit_admin_request(callback: CallbackQuery, state: FSMContext):
    # Запрашиваем у пользователя ввод должности
    await callback.message.answer(
        "Пожалуйста, введите вашу должность для административных прав."
    )

    # Устанавливаем состояние для ожидания ввода должности
    await state.set_state(AdminRequestState.waiting_for_position)

    # Подтверждаем выполнение callback
    await callback.answer()


# Обработчик ввода должности
@router.message(StateFilter(AdminRequestState.waiting_for_position))
async def process_position(message: Message, state: FSMContext):
    # Получаем Telegram ID пользователя
    telegram_id = message.from_user.id

    try:
        # Находим пользователя в базе данных
        user = await sync_to_async(User.objects.get)(telegram_id=telegram_id)

        # Проверяем, есть ли у пользователя активная заявка на административные права
        admin_request_exists = await sync_to_async(AdminRequest.objects.filter(user=user).exists)()
        if admin_request_exists:
            # Если заявка существует, сообщаем об этом
            await message.answer(
                "Ваша заявка на административные права уже находится на рассмотрении. Пожалуйста, ожидайте."
            )
        else:
            # Если заявки нет, создаем новую
            admin_request = await sync_to_async(AdminRequest.objects.create)(
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