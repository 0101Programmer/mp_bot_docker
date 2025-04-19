from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from ...models import Appeal, StatusChoices
from ...tools.main_logger import logger

PREVIEW_LENGTH = 300  # Количество символов для предпросмотра текста обращения

class AppealState(StatesGroup):
    waiting_for_id = State()

# Клавиатура для обращения
def get_appeal_keyboard(appeal_id: int, status: str, show_full_text: bool = False, text_length: int = 0, has_file: bool = False):
    builder = InlineKeyboardBuilder()

    # Если текст длинный и свёрнут, добавляем кнопку "Показать полностью" с эмодзи 🔍
    if text_length > PREVIEW_LENGTH and not show_full_text:
        builder.button(text="🔍 Показать полностью", callback_data=f"appeal_show_full_{appeal_id}")

    # Если текст развёрнут, добавляем кнопку "Свернуть" с эмодзи ↩️
    elif text_length > PREVIEW_LENGTH and show_full_text:
        builder.button(text="↩️ Свернуть", callback_data=f"appeal_collapse_{appeal_id}")

    # Добавляем кнопку "Посмотреть файл" с эмодзи 📎, если файл существует
    if has_file:
        builder.button(text="📎 Посмотреть файл", callback_data=f"appeal_view_file_{appeal_id}")

    # Добавляем основные кнопки только если текст свёрнут или его длина <= PREVIEW_LENGTH
    if text_length <= PREVIEW_LENGTH or not show_full_text:
        if status == StatusChoices.NEW:  # Используем константу NEW
            builder.button(text="✅ Принять", callback_data=f"appeal_accept_{appeal_id}")
            builder.button(text="❌ Отклонить", callback_data=f"appeal_reject_{appeal_id}")
        builder.button(text="🗑️ Удалить", callback_data=f"appeal_delete_{appeal_id}")

    builder.adjust(1)  # Кнопки будут расположены по одной в строке
    return builder.as_markup()

# Функция для формирования текста ответа
def format_appeal_response(appeal, user_info: str, commission_name: str, preview_text: str, status_display: str) -> str:
    """
    Формирует текстовое представление обращения с HTML-форматированием и эмодзи.
    :param appeal: Объект обращения.
    :param user_info: Информация о пользователе.
    :param commission_name: Название комиссии.
    :param preview_text: Предварительный текст обращения (сокращенный или полный).
    :param status_display: Текстовое представление статуса.
    :return: Отформатированный текст.
    """
    return (
        f"📋 <b>Обращение #{appeal.id}</b>\n\n"
        f"👤 <b>Пользователь:</b> {user_info}\n\n"
        f"📚 <b>Комиссия:</b> {commission_name}\n\n"
        f"📝 <b>Текст обращения:</b>\n{preview_text}\n\n"
        f"📞 <b>Контактная информация:</b> {appeal.contact_info or 'Не указана'}\n\n"
        f"📊 <b>Статус:</b> {status_display}"
    )

# Функция для формирования данных обращения, пользователя, комиссии и статуса
async def get_appeal_details(appeal_id: int):
    """
    Получает детали обращения, включая данные пользователя, комиссию и текстовый статус.
    :param appeal_id: ID обращения.
    :return: Кортеж (обращение, имя пользователя, название комиссии, текстовый статус).
    """
    # Получаем обращение с использованием select_related
    appeal = await sync_to_async(Appeal.objects.select_related('user', 'commission').get)(id=appeal_id)

    # Получаем данные пользователя через sync_to_async
    user_info = await sync_to_async(lambda: appeal.user.username if appeal.user else "Неизвестен")()

    # Получаем название комиссии через sync_to_async
    commission_name = await sync_to_async(lambda: appeal.commission.name if appeal.commission else "Комиссия не указана")()

    # Определяем текст статуса из APPEAL_STATUSES
    status_display = next((status[1] for status in StatusChoices.APPEAL_STATUSES if status[0] == appeal.status), "Неизвестный статус")

    return appeal, user_info, commission_name, status_display

# Функция, которая обновляет статус обращения и отправляет обновленное сообщение
async def update_appeal_status(callback: CallbackQuery, new_status: str):
    """
    Обновляет статус обращения и отправляет обновленное сообщение.
    :param callback: CallbackQuery с данными о нажатии кнопки.
    :param new_status: Новый статус обращения (например, StatusChoices.PROCESSED или StatusChoices.REJECTED).
    """
    appeal_id = int(callback.data.split("_")[2])  # Извлекаем ID обращения из callback_data

    try:
        # Получаем детали обращения
        appeal, user_info, commission_name, status_display = await get_appeal_details(appeal_id)

        # Изменяем статус обращения на новый
        appeal.status = new_status

        # Сохраняем объект, чтобы сработал сигнал pre_save
        await sync_to_async(appeal.save)()

        # Формируем ответ с помощью функции format_appeal_response
        response = format_appeal_response(
            appeal=appeal,
            user_info=user_info,
            commission_name=commission_name,
            preview_text=appeal.appeal_text[:PREVIEW_LENGTH] + "..." if len(appeal.appeal_text) > PREVIEW_LENGTH else appeal.appeal_text,
            status_display=status_display
        )

        # Обновляем сообщение с новым статусом и клавиатурой
        await callback.message.edit_text(
            response,
            reply_markup=get_appeal_keyboard(
                appeal.id,
                appeal.status,
                show_full_text=False,
                text_length=len(appeal.appeal_text),
                has_file=bool(appeal.file_path)  # Проверяем наличие файла
            ),
            parse_mode='HTML'  # Включаем HTML-парсинг
        )

    except Exception as e:
        logger.error(f"Ошибка при обновлении статуса обращения: {e}")
        await callback.message.answer(
            "❌ <b>Произошла ошибка при обработке запроса.</b>\n\n"
            "<i>Пожалуйста, попробуйте позже.</i>",
            parse_mode='HTML'
        )
    finally:
        await callback.answer()  # Убираем подсветку кнопки