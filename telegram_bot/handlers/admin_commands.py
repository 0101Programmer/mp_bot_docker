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


# Команда /admin
@router.message(Command("admin"))
async def admin_command(message: Message):
    # Получаем Telegram ID пользователя
    telegram_id = message.from_user.id

    try:
        # Находим пользователя в базе данных
        user = await sync_to_async(User.objects.get)(telegram_id=telegram_id)

        # Проверяем, является ли пользователь администратором
        if user.is_admin:
            # Создаем инлайн-клавиатуру для администратора
            builder = InlineKeyboardBuilder()
            builder.button(text="Просмотр заявок в ожидании", callback_data="view_pending_requests")
            builder.button(text="Просмотр одобренных заявок", callback_data="view_approved_requests")
            builder.button(text="Просмотр отклонённых заявок", callback_data="view_rejected_requests")
            builder.adjust(1)

            await message.answer("Выберите действие:", reply_markup=builder.as_markup())
        else:
            # Проверяем, есть ли у пользователя активная заявка на административные права
            admin_request_exists = await sync_to_async(AdminRequest.objects.filter(user=user).exists)()
            if admin_request_exists:
                # Если заявка существует, сообщаем об этом
                await message.answer(
                    "Ваша заявка на административные права находится на рассмотрении. Пожалуйста, ожидайте."
                )
            else:
                # Если заявки нет, предлагаем подать новую
                builder = InlineKeyboardBuilder()
                builder.button(text="Подать заявку", callback_data="submit_admin_request")
                builder.adjust(1)

                await message.answer(
                    "У вас нет статуса администратора. Хотите подать заявку?",
                    reply_markup=builder.as_markup()
                )

    except User.DoesNotExist:
        await message.answer("Вы не зарегистрированы. Пожалуйста, начните с команды /start.")


# Обработчик для просмотра заявок в ожидании
@router.callback_query(F.data == "view_pending_requests")
async def view_pending_requests(callback: CallbackQuery):
    # Подтверждаем обработку callback-запроса
    await callback.answer()

    # Получаем все заявки в статусе "pending"
    pending_requests = await sync_to_async(list)(AdminRequest.objects.filter(status='pending'))

    if pending_requests:
        for request in pending_requests:
            # Асинхронно получаем имя пользователя
            username = await sync_to_async(lambda: request.user.username)()
            response = (
                f"Заявка в ожидании:\n"
                f"ID: {request.id}\n"
                f"Пользователь: {username}\n"
                f"Должность: {request.admin_position}"
            )
            await callback.message.answer(response)
    else:
        await callback.message.answer("Нет заявок в ожидании.")


# Обработчик для просмотра одобренных заявок
@router.callback_query(F.data == "view_approved_requests")
async def view_approved_requests(callback: CallbackQuery):
    # Подтверждаем обработку callback-запроса
    await callback.answer()

    # Получаем все заявки в статусе "approved"
    approved_requests = await sync_to_async(list)(AdminRequest.objects.filter(status='approved'))

    if approved_requests:
        for request in approved_requests:
            # Асинхронно получаем имя пользователя
            username = await sync_to_async(lambda: request.user.username)()
            response = (
                f"Одобренная заявка:\n"
                f"ID: {request.id}\n"
                f"Пользователь: {username}\n"
                f"Должность: {request.admin_position}"
            )
            await callback.message.answer(response)
    else:
        await callback.message.answer("Нет одобренных заявок.")


# Обработчик для просмотра отклонённых заявок
@router.callback_query(F.data == "view_rejected_requests")
async def view_rejected_requests(callback: CallbackQuery):
    # Подтверждаем обработку callback-запроса
    await callback.answer()

    # Получаем все заявки в статусе "rejected"
    rejected_requests = await sync_to_async(list)(AdminRequest.objects.filter(status='rejected'))

    if rejected_requests:
        for request in rejected_requests:
            # Асинхронно получаем имя пользователя
            username = await sync_to_async(lambda: request.user.username)()
            response = (
                f"Отклонённая заявка:\n"
                f"ID: {request.id}\n"
                f"Пользователь: {username}\n"
                f"Должность: {request.admin_position}\n"
                f"Комментарий: {request.comment}"
            )
            await callback.message.answer(response)
    else:
        await callback.message.answer("Нет отклонённых заявок.")