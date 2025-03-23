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
            await message.answer("Вы являетесь администратором.")
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