from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from asgiref.sync import sync_to_async
from ...models import AdminRequest, User, Appeal

router = Router()

class AppealState(StatesGroup):
    waiting_for_id = State()

# Обработка кнопки "Просмотр обращений"
@router.callback_query(F.data == "view_appeals")
async def view_appeals(callback: CallbackQuery, state: FSMContext):
    # Отправляем ответ на коллбэк, чтобы убрать подсветку кнопки
    await callback.answer()

    # Запрашиваем ID обращения
    await callback.message.answer("Введите ID обращения (только цифры):")
    await state.set_state(AppealState.waiting_for_id)

# Обработка ввода ID
@router.message(AppealState.waiting_for_id)
async def process_appeal_id(message: Message, state: FSMContext):
    appeal_id = message.text.strip()

    # Проверяем, что введены только цифры
    if not appeal_id.isdigit():
        await message.answer("Некорректный ввод. Введите только цифры:")
        return

    try:
        # Получаем обращение с использованием select_related
        appeal = await sync_to_async(Appeal.objects.select_related('user').get)(id=int(appeal_id))

        # Получаем данные пользователя через sync_to_async
        user_info = await sync_to_async(lambda: appeal.user.username if appeal.user else "Неизвестен")()

        # Формируем ответ
        response = (
            f"Обращение #{appeal.id}\n"
            f"Пользователь: {user_info}\n"
            f"Текст обращения: {appeal.appeal_text}\n"
            f"Контактная информация: {appeal.contact_info or 'Не указана'}\n"
            f"Статус: {appeal.status}"
        )
        await message.answer(response)

    except Appeal.DoesNotExist:
        await message.answer("Обращение с таким ID не найдено.")
    except Exception as e:
        # Логируем ошибку для отладки
        print(f"Произошла ошибка: {e}")
        await message.answer("Произошла ошибка при обработке запроса.")

    # Сбрасываем состояние
    await state.clear()