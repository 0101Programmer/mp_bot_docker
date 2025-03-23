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
    waiting_for_comment = State()  # Состояние для ожидания ввода комментария


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
            builder.button(text="Добавить комиссию", callback_data="add_commission")
            builder.adjust(1)

            await message.answer("Выберите действие:", reply_markup=builder.as_markup())
        else:
            # Проверяем, есть ли у пользователя заявка в ожидании
            pending_request_exists = await sync_to_async(AdminRequest.objects.filter(user=user, status='pending').exists)()
            if pending_request_exists:
                # Если заявка в ожидании существует, сообщаем об этом
                await message.answer(
                    "Ваша заявка на административные права находится на рассмотрении. Пожалуйста, ожидайте."
                )
            else:
                # Проверяем, есть ли отклонённая заявка
                rejected_request_exists = await sync_to_async(
                    AdminRequest.objects.filter(user=user, status='rejected').exists)()
                if rejected_request_exists:
                    # Получаем последнюю отклонённую заявку
                    rejected_request = await sync_to_async(
                        AdminRequest.objects.filter(user=user, status='rejected').last)()

                    # Формируем сообщение с комментарием
                    response = (
                        f"Ваша предыдущая заявка на административные права была отклонена.\n"
                        f"Комментарий: {rejected_request.comment}\n"
                        f"Вы можете подать новую заявку."
                    )

                    # Создаем кнопку для подачи новой заявки
                    builder = InlineKeyboardBuilder()
                    builder.button(text="Подать заявку", callback_data="submit_admin_request")
                    builder.adjust(1)

                    await message.answer(response, reply_markup=builder.as_markup())
                else:
                    # Если заявок нет, предлагаем подать новую
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

            # Создаем инлайн-кнопку "Одобрить"
            builder = InlineKeyboardBuilder()
            builder.button(text="Одобрить", callback_data=f"approve_request:{request.id}")
            builder.button(text="Отклонить", callback_data=f"reject_request:{request.id}")
            builder.adjust(1)

            await callback.message.answer(response, reply_markup=builder.as_markup())
    else:
        await callback.message.answer("Нет заявок в ожидании.")


# Обработчик для кнопки "Одобрить"
@router.callback_query(F.data.startswith("approve_request:"))
async def approve_request(callback: CallbackQuery):
    # Подтверждаем обработку callback-запроса
    await callback.answer()

    # Получаем ID заявки из callback_data
    request_id = int(callback.data.split(":")[1])

    # Находим заявку в базе данных
    request = await sync_to_async(AdminRequest.objects.get)(id=request_id)

    # Меняем статус заявки на "Одобрено"
    request.status = "approved"
    await sync_to_async(request.save)()

    # Отправляем сообщение об успешном одобрении
    await callback.message.answer(f"Заявка ID {request_id} одобрена.")


# Обработчик для кнопки "Отклонить"
@router.callback_query(F.data.startswith("reject_request:"))
async def reject_request(callback: CallbackQuery, state: FSMContext):
    # Подтверждаем обработку callback-запроса
    await callback.answer()

    # Получаем ID заявки из callback_data
    request_id = int(callback.data.split(":")[1])

    # Сохраняем ID заявки в состоянии
    await state.update_data(request_id=request_id)

    # Переходим в состояние ожидания комментария
    await state.set_state(AdminRequestState.waiting_for_comment)

    # Запрашиваем комментарий
    await callback.message.answer("Введите комментарий для отклонения заявки:")


# Обработчик для ввода комментария
@router.message(AdminRequestState.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()
    request_id = data["request_id"]

    # Находим заявку в базе данных
    request = await sync_to_async(AdminRequest.objects.get)(id=request_id)

    # Меняем статус заявки на "Отклонено" и сохраняем комментарий
    request.status = "rejected"
    request.comment = message.text
    await sync_to_async(request.save)()

    # Сбрасываем состояние
    await state.clear()

    # Отправляем сообщение об успешном отклонении
    await message.answer(f"Заявка ID {request_id} отклонена с комментарием: {message.text}")


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