from html import escape
from typing import Callable, Awaitable

from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from decouple import config
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _

from ...models import Appeal, StatusChoices
from ...models import CommissionInfo, User
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

# ===================== КОНФИГ ДЛЯ НАПИСАНИЯ ОБРАЩЕНИЙ =====================

# Паттерны для проверки email и номера телефона
EMAIL_PATTERN = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
PHONE_PATTERN = r'^\+7\d{10}$'  # Российский номер в международном формате: +7XXXXXXXXXX

# Длинна текста
MIN_TXT_LENGTH = int(config('MIN_TXT_LENGTH'))
MAX_TXT_LENGTH = int(config('MAX_TXT_LENGTH'))

# Максимальный размер файла (в байтах)
MAX_FILE_SIZE = int(config('MAX_FILE_SIZE'))

# Функция для сохранения обращения в базу данных
@sync_to_async
def save_appeal_to_db(data, telegram_id, django_file=None, original_file_name=None):
    """
    Сохраняет обращение в базу данных.
    """
    try:
        # Получаем пользователя по telegram_id
        user = User.objects.get(telegram_id=telegram_id)
    except ObjectDoesNotExist:
        raise ValueError("Пользователь с указанным telegram_id не найден.")

    try:
        # Получаем комиссию по ID
        commission = CommissionInfo.objects.get(id=data["commission_id"])
    except ObjectDoesNotExist:
        raise ValueError("Комиссия с указанным ID не найдена.")

    # Создаем объект обращения
    appeal = Appeal(
        user=user,
        commission=commission,
        appeal_text=data["appeal_text"],
        contact_info=data.get("contact_info"),
        status=StatusChoices.NEW
    )

    # Если файл передан, сохраняем его
    if django_file and original_file_name:
        appeal.file_path.save(original_file_name, django_file)

    # Сохраняем обращение в базу данных
    appeal.save()
    return appeal

# Класс для хранения состояний
class AppealForm(StatesGroup):
    choosing_commission = State()  # Выбор комиссии
    choosing_contact_option = State()  # Выбор контактов или анонимности
    entering_contact_info = State()  # Ввод контактной информации
    writing_appeal = State()  # Написание обращения
    attaching_file = State()  # Прикрепление файла