from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from .utils import generate_commissions_keyboard

from ...models import CommissionInfo
from ...tools.main_logger import logger

router = Router()

# Обработчик текста "Описание комиссий"
@router.message(F.text == "Описание комиссий")
async def show_commissions(message: Message):
    """
    Обработчик для кнопки "Описание комиссий".
    Отправляет список комиссий с inline-кнопками.
    """
    try:
        # Получаем все комиссии из базы данных
        commissions = await sync_to_async(list)(CommissionInfo.objects.all())

        if not commissions:
            await message.answer("Список комиссий пуст.")
            return

        # Генерируем клавиатуру с помощью функции
        markup = generate_commissions_keyboard(commissions)

        # Отправляем сообщение с inline-клавиатурой
        await message.answer(
            "<b>Выберите комиссию для получения информации:</b>",
            reply_markup=markup,
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Ошибка при получении списка комиссий: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик выбора конкретной комиссии
@router.callback_query(F.data.startswith("info_commission:"))
async def show_commission_info(callback_query: CallbackQuery):
    """
    Обработчик для выбора конкретной комиссии.
    Отправляет описание комиссии с кнопкой "Назад".
    """
    try:
        # Извлекаем ID комиссии из callback_data
        commission_id = int(callback_query.data.split(":")[1])

        # Находим комиссию в базе данных
        commission = await sync_to_async(CommissionInfo.objects.get)(id=commission_id)

        # Формируем ответное сообщение с HTML-стилизацией, эмодзи и увеличенными межстрочными интервалами
        response = (
            f"📋 <b>Комиссия:</b> {commission.name}\n\n"  # Добавляем пустую строку после названия
            f"🔢 <b>ID комиссии:</b> <code>{commission.id}</code>\n\n"  # Добавляем пустую строку после ID
            f"📅 <b>Дата создания:</b> <i>{commission.created_at.strftime('%d.%m.%Y %H:%M')}</i>\n\n"  # Добавляем пустую строку после даты
            f"📝 <b>Описание:</b>\n{commission.description or '<i>Описание отсутствует.</i>'}"  # Описание без дополнительных строк
        )

        # Создаем inline-клавиатуру с кнопкой "Назад" (добавляем эмодзи 🔙)
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_commissions")]
            ]
        )

        # Редактируем сообщение с описанием комиссии и кнопкой "Назад"
        await callback_query.message.edit_text(
            text=response,
            reply_markup=markup,
            parse_mode='HTML'  # Передаем parse_mode как строку
        )

    except CommissionInfo.DoesNotExist:
        await callback_query.message.edit_text("Комиссия не найдена. Попробуйте снова.")
    except Exception as e:
        logger.error(f"Ошибка при получении информации о комиссии: {e}")
        await callback_query.message.edit_text("Произошла ошибка. Пожалуйста, попробуйте позже.")


# Обработчик inline-кнопки "Назад"
@router.callback_query(F.data == "back_to_commissions")
async def go_back_to_commissions(callback_query: CallbackQuery):
    """
    Обработчик для кнопки "Назад".
    Возвращает пользователя к списку комиссий.
    """
    try:
        # Получаем все комиссии из базы данных
        commissions = await sync_to_async(list)(CommissionInfo.objects.all())

        if not commissions:
            await callback_query.message.edit_text("Список комиссий пуст.")
            return

        # Генерируем клавиатуру с помощью функции
        markup = generate_commissions_keyboard(commissions)

        # Редактируем сообщение для возврата к списку комиссий
        await callback_query.message.edit_text(
            "<b>Выберите комиссию для получения информации:</b>",
            reply_markup=markup,
            parse_mode='HTML'
        )

    except Exception as e:
        logger.error(f"Ошибка при возврате к списку комиссий: {e}")
        await callback_query.message.edit_text("Произошла ошибка. Пожалуйста, попробуйте позже.")