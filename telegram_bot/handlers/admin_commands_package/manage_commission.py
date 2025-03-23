from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
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


# Обработчик для удаления комиссии
@router.callback_query(F.data == "delete_commissions")
async def delete_commissions(callback: CallbackQuery):
    # Получаем все комиссии из базы данных
    commissions = await sync_to_async(list)(CommissionInfo.objects.all())

    if commissions:
        # Создаем инлайн-клавиатуру для каждой комиссии
        builder = InlineKeyboardBuilder()
        for commission in commissions:
            builder.button(
                text=f"❌ {commission.name}",  # Добавляем иконку "❌" для удаления
                callback_data=f"confirm_delete_commission:{commission.id}"
            )
        builder.button(text="Назад", callback_data="back_to_main_menu")  # Кнопка "Назад"
        builder.adjust(1)  # Располагаем кнопки по одной в строке

        # Отправляем сообщение с кнопками
        await callback.message.edit_text("Выберите комиссию для удаления:", reply_markup=builder.as_markup())
    else:
        # Если комиссий нет, сообщаем об этом
        await callback.message.edit_text("Комиссии отсутствуют.")


# Обработчик для подтверждения удаления комиссии
@router.callback_query(F.data.startswith("confirm_delete_commission:"))
async def confirm_delete_commission(callback: CallbackQuery):
    # Получаем ID комиссии из callback_data
    commission_id = int(callback.data.split(":")[1])

    # Получаем комиссию из базы данных
    commission = await sync_to_async(CommissionInfo.objects.get)(id=commission_id)

    # Создаем клавиатуру для подтверждения удаления
    builder = InlineKeyboardBuilder()
    builder.button(text="Да, удалить", callback_data=f"delete_commission:{commission.id}")
    builder.button(text="Отмена", callback_data="delete_commissions")
    builder.adjust(2)

    # Запрашиваем подтверждение удаления
    await callback.message.edit_text(
        f"Вы уверены, что хотите удалить комиссию '{commission.name}'?",
        reply_markup=builder.as_markup()
    )


# Обработчик для удаления комиссии
@router.callback_query(F.data.startswith("delete_commission:"))
async def delete_commission(callback: CallbackQuery):
    # Получаем ID комиссии из callback_data
    commission_id = int(callback.data.split(":")[1])

    # Удаляем комиссию из базы данных
    await sync_to_async(CommissionInfo.objects.filter(id=commission_id).delete)()

    # Подтверждаем удаление
    await callback.answer(f"Комиссия удалена.")

    # Возвращаем пользователя к списку комиссий для удаления
    await delete_commissions(callback)