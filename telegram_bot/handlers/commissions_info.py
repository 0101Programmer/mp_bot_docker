from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, F
from asgiref.sync import sync_to_async
import logging
from ..models import CommissionInfo  # Импортируем модель CommissionInfo

logger = logging.getLogger(__name__)

router = Router()

# Обработчик текста "Описание комиссий"
@router.message(F.text == "Описание комиссий")
async def show_commissions(message: Message):
    try:
        # Получаем все комиссии из базы данных
        commissions = await sync_to_async(list)(CommissionInfo.objects.all())

        if commissions:
            # Создаем inline-клавиатуру с кнопками для каждой комиссии
            keyboard = [
                [InlineKeyboardButton(text=commission.name, callback_data=f"commission:{commission.id}")]
                for commission in commissions
            ]

            # Создаем объект inline-клавиатуры
            markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

            # Отправляем сообщение с inline-клавиатурой
            await message.answer(
                "Выберите комиссию для получения информации:", reply_markup=markup
            )
        else:
            await message.answer("Список комиссий пуст.")

    except Exception as e:
        # Логируем ошибку
        logger.error(f"Ошибка при получении списка комиссий: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик выбора конкретной комиссии
@router.callback_query(F.data.startswith("commission:"))
async def show_commission_info(callback_query, message=None):
    try:
        # Извлекаем ID комиссии из callback_data
        commission_id = int(callback_query.data.split(":")[1])

        # Находим комиссию в базе данных
        commission = await sync_to_async(CommissionInfo.objects.get)(id=commission_id)

        # Формируем ответное сообщение
        response = (
            f"Комиссия: {commission.name}\n\n"
            f"Описание: {commission.description or 'Описание отсутствует.'}"
        )

        # Создаем inline-клавиатуру с кнопкой "Назад"
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Назад", callback_data="back_to_commissions")]
            ]
        )

        # Отправляем сообщение с описанием комиссии и кнопкой "Назад"
        await callback_query.message.edit_text(response, reply_markup=markup)

    except CommissionInfo.DoesNotExist:
        await callback_query.message.edit_text("Комиссия не найдена. Попробуйте снова.")
    except Exception as e:
        # Логируем ошибку
        logger.error(f"Ошибка при получении информации о комиссии: {e}")
        await callback_query.message.edit_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик inline-кнопки "Назад"
@router.callback_query(F.data == "back_to_commissions")
async def go_back_to_commissions(callback_query):
    try:
        # Получаем все комиссии из базы данных
        commissions = await sync_to_async(list)(CommissionInfo.objects.all())

        if commissions:
            # Создаем inline-клавиатуру с кнопками для каждой комиссии
            keyboard = [
                [InlineKeyboardButton(text=commission.name, callback_data=f"commission:{commission.id}")]
                for commission in commissions
            ]

            # Создаем объект inline-клавиатуры
            markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

            # Редактируем сообщение для возврата к списку комиссий
            await callback_query.message.edit_text(
                "Выберите комиссию для получения информации:", reply_markup=markup
            )
        else:
            await callback_query.message.edit_text("Список комиссий пуст.")

    except Exception as e:
        # Логируем ошибку
        logger.error(f"Ошибка при возврате к списку комиссий: {e}")
        await callback_query.message.edit_text("Произошла ошибка. Пожалуйста, попробуйте позже.")