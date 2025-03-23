from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from asgiref.sync import sync_to_async
from ...models import CommissionInfo

# Создаем роутер для обработки команд
router = Router()

# Определяем состояния для добавления комиссии
class AddCommissionState(StatesGroup):
    waiting_for_name = State()  # Ожидание ввода названия комиссии
    waiting_for_description = State()  # Ожидание ввода описания комиссии


# Обработчик для начала добавления комиссии
@router.callback_query(F.data == "add_commission")
async def start_add_commission(callback: CallbackQuery, state: FSMContext):
    # Подтверждаем обработку callback-запроса
    await callback.answer()

    # Переходим в состояние ожидания ввода названия
    await state.set_state(AddCommissionState.waiting_for_name)

    # Запрашиваем название комиссии
    await callback.message.answer("Введите название комиссии:")


# Обработчик для ввода названия комиссии
@router.message(AddCommissionState.waiting_for_name)
async def process_commission_name(message: Message, state: FSMContext):
    # Сохраняем название комиссии в состоянии
    await state.update_data(name=message.text)

    # Переходим в состояние ожидания ввода описания
    await state.set_state(AddCommissionState.waiting_for_description)

    # Запрашиваем описание комиссии
    await message.answer("Введите описание комиссии:")


# Обработчик для ввода описания комиссии
@router.message(AddCommissionState.waiting_for_description)
async def process_commission_description(message: Message, state: FSMContext):
    # Получаем данные из состояния
    data = await state.get_data()
    name = data["name"]
    description = message.text

    # Создаем новую комиссию в базе данных
    await sync_to_async(CommissionInfo.objects.create)(name=name, description=description)

    # Сбрасываем состояние
    await state.clear()

    # Отправляем сообщение об успешном добавлении
    await message.answer(f"Комиссия '{name}' успешно добавлена!")