from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.db.utils import IntegrityError

from ...models import CommissionInfo

# Создаем роутер для обработки команд
router = Router()


# Определяем состояния для добавления комиссии
class AddCommissionState(StatesGroup):
    waiting_for_name = State()  # Ожидание ввода названия комиссии
    waiting_for_description = State()  # Ожидание ввода описания комиссии


# Обработчик для выбора "Действия с комиссиями"
@router.callback_query(F.data == "commission_actions")
async def commission_actions_menu(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text="Добавить комиссию", callback_data="add_commission")
    builder.button(text="Удалить комиссию", callback_data="delete_commissions")
    builder.button(text="Назад", callback_data="back_to_main_menu")
    builder.adjust(1)

    await callback.message.edit_text("Выберите действие с комиссиями:", reply_markup=builder.as_markup())


# Обработчик для начала добавления комиссии
@router.callback_query(F.data == "add_commission")
async def start_add_commission(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AddCommissionState.waiting_for_name)
    await callback.message.answer("Введите название комиссии:")


# Обработчик для ввода названия комиссии
@router.message(AddCommissionState.waiting_for_name)
async def process_commission_name(message: Message, state: FSMContext):
    commission_name = message.text.strip()

    # Проверяем существование комиссии с таким названием
    commission_exists = await sync_to_async(CommissionInfo.objects.filter(name=commission_name).exists)()

    if commission_exists:
        await message.answer(
            f"❌ Комиссия с названием <b>'{commission_name}'</b> уже существует.\n"
            "Пожалуйста, введите другое название:",
            parse_mode="HTML"
        )
        return

    await state.update_data(name=commission_name)
    await state.set_state(AddCommissionState.waiting_for_description)
    await message.answer("📝 Введите описание комиссии:")


# Обработчик для ввода описания комиссии и сохранения
@router.message(AddCommissionState.waiting_for_description)
async def process_commission_description(message: Message, state: FSMContext):
    data = await state.get_data()
    commission_name = data.get('name')
    commission_description = message.text.strip()

    try:
        # Создаем новую комиссию
        await sync_to_async(CommissionInfo.objects.create)(
            name=commission_name,
            description=commission_description
        )

        await message.answer(
            f"✅ Комиссия <b>'{commission_name}'</b> успешно создана!\n\n"
            f"<b>Название:</b> {commission_name}\n"
            f"<b>Описание:</b> {commission_description}",
            parse_mode="HTML"
        )

    except IntegrityError:
        await message.answer(
            f"❌ Ошибка: комиссия с названием '{commission_name}' уже существует. "
            "Пожалуйста, начните процесс заново с другого названия."
        )
    except Exception as e:
        await message.answer(f"⚠️ Произошла непредвиденная ошибка: {str(e)}")
    finally:
        await state.clear()


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