from html import escape

from aiogram import Router, F
from aiogram.types import FSInputFile, InlineKeyboardButton
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.utils.translation import gettext as _
from aiogram.types import CallbackQuery

from .utils import (
    process_appeal,
    SEPARATOR,
    FULL_APPEAL_HEADER,
    FULL_STATUS_LINE,
    FULL_COMMISSION_LINE,
    FULL_TEXT_HEADER,
    FILE_ATTACHMENT_LINE,
    APPEAL_STATUS_MAPPING, generate_appeal_response
)
from ...models import Appeal
from ...tools.main_logger import logger

router = Router()


@router.message(F.text == "Отследить статус обращения")
async def track_appeal_status(message: Message, user=None):
    """
    Обработчик для кнопки "Отследить статус обращения".
    """
    try:
        # Получаем обращения с предзагрузкой комиссии
        appeals = await sync_to_async(list)(
            Appeal.objects.filter(user=user)
            .select_related('commission')
            .order_by('-id')  # Сначала новые
        )

        if not appeals:
            await message.answer("У вас пока нет обращений.")
            return

        builder = InlineKeyboardBuilder()

        for appeal in appeals:
            # Получаем данные статуса
            status_data = APPEAL_STATUS_MAPPING.get(appeal.status.lower(), {
                'display': appeal.status,
                'emoji': '📄'
            })

            # Формируем текст кнопки
            button_text = (
                f"№{appeal.id} | {status_data['emoji']} {status_data['display']} | "
                f"{escape(appeal.commission.name)}"
            )

            builder.add(InlineKeyboardButton(
                text=button_text,
                callback_data=f"appeal_detail:{appeal.id}"
            ))

        builder.adjust(1)  # По одной кнопке в ряд

        await message.answer(
            "📋 Ваши обращения:",
            reply_markup=builder.as_markup()
        )

    except Exception as e:
        logger.error(f"Error in track_appeal_status: {e}")
        await message.answer("⚠️ Произошла ошибка при получении обращений.")


@router.callback_query(F.data.startswith("appeal_detail:"))
async def show_appeal_detail(callback: CallbackQuery):
    try:
        appeal_id = int(callback.data.split(":")[1])
        appeal = await sync_to_async(
            Appeal.objects.select_related('commission').get
        )(id=appeal_id)

        # Генерируем ответ и клавиатуру
        response, builder = await generate_appeal_response(appeal)

        # Отправляем сообщение с HTML-разметкой
        await callback.message.answer(
            response,
            reply_markup=builder.as_markup(),
            parse_mode='HTML'  # Добавляем парсинг HTML
        )
        await callback.answer()

    except Appeal.DoesNotExist:
        await callback.answer("❌ Обращение не найдено!", show_alert=True)
    except Exception as e:
        logger.error(f"Error in show_appeal_detail: {e}")
        await callback.answer("⚠️ Произошла ошибка при загрузке обращения!", show_alert=True)


# Обработчик для кнопки "Посмотреть файл"
@router.callback_query(F.data.startswith("view_file:"))
async def view_file(callback_query: CallbackQuery):
    try:
        # Извлекаем ID обращения из callback_data
        appeal_id = int(callback_query.data.split(":")[1])

        # Находим обращение в базе данных
        appeal = await sync_to_async(Appeal.objects.get)(id=appeal_id)

        # Проверяем, существует ли файл
        if appeal.file_path and appeal.file_path.storage.exists(appeal.file_path.name):
            # Отправляем файл пользователю
            file_path = appeal.file_path.path  # Полный путь к файлу
            file = FSInputFile(file_path)
            await callback_query.message.answer_document(file)
        else:
            # Если файл не найден, отправляем сообщение об ошибке
            await callback_query.message.answer("Файл не найден.")

        # Убираем часы загрузки (подтверждаем выполнение callback)
        await callback_query.answer()

    except Appeal.DoesNotExist:
        await callback_query.answer("Обращение не найдено.", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка при просмотре файла: {e}")
        await callback_query.answer("Произошла ошибка. Пожалуйста, попробуйте позже.", show_alert=True)


# Обработчик нажатия на кнопку "Показать полностью"
@router.callback_query(F.data.startswith("show_full:"))
async def show_full_appeal(callback: CallbackQuery):
    try:
        appeal_id = int(callback.data.split(":")[1])
        appeal = await sync_to_async(
            Appeal.objects.select_related('commission').get
        )(id=appeal_id)

        # Получаем данные статуса
        status_data = APPEAL_STATUS_MAPPING.get(appeal.status.lower(), {
            'display': appeal.status,
            'emoji': '📄'
        })

        # Экранируем данные
        commission_name = escape(appeal.commission.name) if appeal.commission else _("Не указана")
        appeal_text = escape(appeal.appeal_text)

        # Формируем полную версию из шаблонов
        full_response = (
            FULL_APPEAL_HEADER.format(id=appeal_id, separator=SEPARATOR) +
            FULL_STATUS_LINE.format(emoji=status_data['emoji'], status=escape(status_data['display'])) +
            FULL_COMMISSION_LINE.format(commission=commission_name) +
            FULL_TEXT_HEADER.format(text=appeal_text)
        )

        # Добавляем информацию о файле если есть
        if appeal.file_path:
            full_response += FILE_ATTACHMENT_LINE

        # Создаем клавиатуру
        full_builder = InlineKeyboardBuilder()
        full_builder.button(
            text="↩️ Свернуть",
            callback_data=f"collapse:{appeal_id}"
        )
        if appeal.file_path:
            full_builder.button(
                text="📎 Открыть файл",
                callback_data=f"view_file:{appeal_id}"
            )
        full_builder.adjust(1)

        # Редактируем сообщение
        await callback.message.edit_text(
            full_response,
            reply_markup=full_builder.as_markup(),
            parse_mode='HTML'
        )
        await callback.answer()

    except Appeal.DoesNotExist:
        await callback.answer("❌ Обращение не найдено", show_alert=True)
    except Exception as e:
        logger.error(f"Error in show_full_appeal: {e}", exc_info=True)
        await callback.answer("⚠️ Ошибка при загрузке полного текста", show_alert=True)


# Обработчик нажатия на кнопку "Свернуть"
@router.callback_query(F.data.startswith("collapse:"))
async def collapse_appeal(callback: CallbackQuery):
    await process_appeal(
        callback=callback,
        response_message="↩️ Обращение свернуто",
        error_message="⚠️ Не удалось свернуть обращение"
    )


# Обработчик нажатия на кнопку "Удалить"
@router.callback_query(F.data.startswith("delete_appeal:"))
async def request_delete_confirmation(callback: CallbackQuery):
    try:
        appeal_id = int(callback.data.split(":")[1])

        builder = InlineKeyboardBuilder()
        builder.button(
            text="🗑 Удалить",
            callback_data=f"confirm_delete:{appeal_id}"
        )
        builder.button(
            text="◀️ Отменить",
            callback_data=f"cancel_delete:{appeal_id}"
        )
        builder.adjust(2)

        await callback.message.edit_text(
            "❓ Вы уверены, что хотите удалить обращение?",
            reply_markup=builder.as_markup()
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Delete confirmation error: {e}")
        await callback.answer("⚠️ Ошибка запроса", show_alert=True)


# Обработчик подтверждения удаления
@router.callback_query(F.data.startswith("confirm_delete:"))
async def confirm_delete_appeal(callback: CallbackQuery):
    try:
        appeal_id = int(callback.data.split(":")[1])
        appeal = await sync_to_async(Appeal.objects.get)(id=appeal_id)

        # Удаляем файл, если он есть (с улучшенным логированием)
        if appeal.file_path:
            try:
                file_path = appeal.file_path.name
                storage = appeal.file_path.storage
                await sync_to_async(storage.delete)(file_path)
                logger.info(f"Файл обращения {appeal_id} успешно удалён: {file_path}")
            except Exception as file_error:
                logger.error(f"Ошибка удаления файла обращения {appeal_id}: {file_error}")

        # Удаляем запись
        await sync_to_async(appeal.delete)()
        logger.info(f"Обращение {appeal_id} успешно удалено")

        # Форматируем сообщение об успехе с HTML
        success_message = (
            f"<b>✅ Обращение №{appeal_id} удалено</b>\n\n"
            f"<i>Все данные и прикреплённые файлы были безвозвратно удалены.</i>"
        )

        # Обновляем сообщение
        await callback.message.edit_text(
            success_message,
            reply_markup=None,
            parse_mode='HTML'  # Добавляем поддержку HTML
        )
        await callback.answer("Обращение удалено")

    except Appeal.DoesNotExist:
        error_message = (
            f"<b>❌ Обращение №{appeal_id} не найдено</b>\n\n"
            f"Возможно, оно было удалено ранее."
        )
        await callback.message.edit_text(
            error_message,
            parse_mode='HTML'
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка удаления обращения {appeal_id}: {e}", exc_info=True)
        error_message = (
            f"<b>⚠️ Ошибка при удалении обращения №{appeal_id}</b>\n\n"
            f"Попробуйте позже или обратитесь к администратору."
        )
        await callback.message.edit_text(
            error_message,
            parse_mode='HTML'
        )
        await callback.answer()


# Обработчик отмены удаления
@router.callback_query(F.data.startswith("cancel_delete:"))
async def cancel_delete_appeal(callback: CallbackQuery):
    await process_appeal(
        callback=callback,
        response_message="❌ Удаление отменено",
        error_message="⚠️ Не удалось отменить удаление"
    )