from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from ..models import AdminRequest, User

# Создаем роутер для обработки команд
router = Router()

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
            # Создаем начальное меню для администратора
            builder = InlineKeyboardBuilder()
            builder.button(text="Заявки на получение администратора", callback_data="admin_requests")
            builder.button(text="Действия с комиссиями", callback_data="commission_actions")
            builder.button(text="Просмотр обращений", callback_data="view_appeals")
            builder.button(text="Действия с пользователями", callback_data="user_actions")
            builder.adjust(1)

            await message.answer("Выберите категорию:", reply_markup=builder.as_markup())
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



# Обработчик для кнопки "Назад"
@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: CallbackQuery):
    # Создаем начальное меню для администратора
    builder = InlineKeyboardBuilder()
    builder.button(text="Заявки на получение администратора", callback_data="admin_requests")
    builder.button(text="Действия с комиссиями", callback_data="commission_actions")
    builder.button(text="Просмотр обращений", callback_data="view_appeals")
    builder.button(text="Действия с пользователями", callback_data="user_actions")
    builder.adjust(1)

    # Редактируем сообщение, чтобы вернуться к начальному меню
    await callback.message.edit_text("Выберите категорию:", reply_markup=builder.as_markup())