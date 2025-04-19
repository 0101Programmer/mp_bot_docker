from html import escape
from typing import Callable, Awaitable

from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _

from ...models import Appeal, StatusChoices
from ...tools.main_logger import logger

# ===================== КОНСТАНТЫ ФОРМАТИРОВАНИЯ =====================
PREVIEW_LENGTH = 300  # Количество символов для предпросмотра текста обращения
DATE_FORMAT = "%d.%m.%Y %H:%M"  # Формат отображения дат

# Разделительная линия для сообщений
SEPARATOR = "<i>────────────────</i>"

# Шаблоны строк для недлинного текста
APPEAL_HEADER = "<b>📌 Обращение №{id}</b>\n{separator}\n"
STATUS_LINE = "{emoji} <b>Статус:</b> {status}\n\n"
COMMISSION_LINE = "👥 <b>Комиссия:</b> {commission}\n\n"
TEXT_HEADER = "📝 <b>Текст обращения:</b>\n<code>{text}</code>\n\n"
CONTACTS_LINE = "📞 <b>Контакты:</b> {contacts}\n\n"
DATES_LINE = "📅 <b>Создано:</b> {created_at}\n🔄 <b>Обновлено:</b> {updated_at}"

# Шаблоны строк для длинного текста
FULL_APPEAL_HEADER = "<b>📌 Обращение №{id}</b>\n{separator}\n"
FULL_STATUS_LINE = "{emoji} <b>Статус:</b> {status}\n\n"
FULL_COMMISSION_LINE = "👥 <b>Комиссия:</b> {commission}\n\n"
FULL_TEXT_HEADER = "📝 <b>Полный текст обращения:</b>\n<code>{text}</code>\n\n"
FILE_ATTACHMENT_LINE = "\n📎 <i>Прикреплён документ</i>"

# Словарь для соответствия статусов обращений и их отображения
APPEAL_STATUS_MAPPING = {
    StatusChoices.NEW: {
        'display': _('Новое'),
        'emoji': '🆕'
    },
    StatusChoices.PROCESSED: {
        'display': _('Обработано'),
        'emoji': '✅'
    },
    StatusChoices.REJECTED: {
        'display': _('Отклонено'),
        'emoji': '❌'
    }
}

# ===================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====================

async def generate_appeal_response(appeal: Appeal) -> tuple[str, InlineKeyboardBuilder]:
    """
    Генерирует текст ответа и клавиатуру для обращения.
    Возвращает кортеж (текст, клавиатура)
    """
    # Получаем данные статуса
    status_data = APPEAL_STATUS_MAPPING.get(appeal.status.lower(), {
        'display': appeal.status,
        'emoji': '📄'
    })

    # Экранируем и форматируем данные
    commission_name = escape(appeal.commission.name) if appeal.commission else _("Не указана")
    needs_expansion = len(appeal.appeal_text) > PREVIEW_LENGTH
    display_text = escape(appeal.appeal_text[:PREVIEW_LENGTH] + ("..." if needs_expansion else ""))
    contact_info = escape(appeal.contact_info) if appeal.contact_info else _('Не указана')

    # Форматируем даты
    created_at = appeal.created_at.strftime(DATE_FORMAT)
    updated_at = appeal.updated_at.strftime(DATE_FORMAT)

    # Собираем сообщение из шаблонов
    response = (
        APPEAL_HEADER.format(id=appeal.id, separator=SEPARATOR) +
        STATUS_LINE.format(emoji=status_data['emoji'], status=escape(status_data['display'])) +
        COMMISSION_LINE.format(commission=commission_name) +
        TEXT_HEADER.format(text=display_text) +
        CONTACTS_LINE.format(contacts=contact_info) +
        SEPARATOR + "\n" +
        DATES_LINE.format(created_at=created_at, updated_at=updated_at)
    )

    # Создаем клавиатуру
    builder = InlineKeyboardBuilder()

    # Добавляем кнопки
    if needs_expansion:
        builder.button(text=f"📄 {_('Показать полностью')}", callback_data=f"show_full:{appeal.id}")
    builder.button(text=f"🗑 {_('Удалить')}", callback_data=f"delete_appeal:{appeal.id}")
    if appeal.file_path:
        builder.button(text=f"📎 {_('Открыть файл')}", callback_data=f"view_file:{appeal.id}")
    builder.adjust(1)

    return response, builder


async def process_appeal(
        callback: CallbackQuery,
        response_message: str,
        error_message: str,
        success_action: Callable[[CallbackQuery], Awaitable[None]] = None
):
    """
    Общая функция для обработки обращений.

    :param callback: CallbackQuery объект
    :param response_message: Сообщение для успешного ответа пользователю
    :param error_message: Сообщение об ошибке при проблемах
    :param success_action: Дополнительное действие после успешной обработки
    """
    try:
        # Извлекаем ID обращения из данных колбэка
        appeal_id = int(callback.data.split(":")[1])

        # Получаем полные данные обращения
        appeal = await sync_to_async(
            Appeal.objects.select_related('commission').get
        )(id=appeal_id)

        # Генерируем стандартный ответ с HTML-разметкой
        response, builder = await generate_appeal_response(appeal)

        # Обновляем сообщение с указанием HTML-парсинга
        await callback.message.edit_text(
            response,
            reply_markup=builder.as_markup(),
            parse_mode='HTML'  # Поддержка HTML-разметки
        )

        # Вызываем дополнительное действие, если оно указано
        if success_action:
            await success_action(callback)

        # Отправляем ответ пользователю
        await callback.answer(response_message)

    except Appeal.DoesNotExist:
        await callback.answer("❌ Обращение не найдено", show_alert=True)
    except Exception as e:
        logger.error(f"Error in process_appeal: {e}", exc_info=True)
        await callback.answer(error_message, show_alert=True)