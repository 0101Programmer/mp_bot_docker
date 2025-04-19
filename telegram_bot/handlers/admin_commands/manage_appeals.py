import os

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from asgiref.sync import sync_to_async

from .utils import PREVIEW_LENGTH, AppealState, get_appeal_details, get_appeal_keyboard, update_appeal_status, \
    format_appeal_response
from ...models import Appeal, StatusChoices
from ...tools.main_logger import logger

router = Router()

# Обработка кнопки "Просмотр обращений"
@router.callback_query(F.data == "view_appeals")
async def view_appeals(callback: CallbackQuery, state: FSMContext):
    # Отправляем ответ на коллбэк, чтобы убрать подсветку кнопки
    await callback.answer()

    # Отправляем сообщение с запросом ID обращения и эмодзи
    await callback.message.answer(
        "🔍 <b>Введите ID обращения:</b>\n\n"
        "<i>(Пример: 123)</i>",
        parse_mode='HTML'  # Включаем HTML-парсинг
    )
    await state.set_state(AppealState.waiting_for_id)


# Обработка ввода ID
@router.message(AppealState.waiting_for_id)
async def process_appeal_id(message: Message, state: FSMContext):
    appeal_id = message.text.strip()

    # Проверяем, что введены только цифры
    if not appeal_id.isdigit():
        await message.answer(
            "❌ <b>Некорректный ввод.</b>\n\n"
            "<i>Введите только цифры:</i>",
            parse_mode='HTML'
        )
        return

    try:
        # Получаем детали обращения с помощью функции get_appeal_details
        appeal, user_info, commission_name, status_display = await get_appeal_details(int(appeal_id))

        # Определяем, нужно ли обрезать текст
        full_text = appeal.appeal_text
        preview_text = full_text[:PREVIEW_LENGTH] + "..." if len(full_text) > PREVIEW_LENGTH else full_text
        show_full_text = len(full_text) <= PREVIEW_LENGTH

        # Формируем текст ответа с помощью функции
        response = format_appeal_response(
            appeal=appeal,
            user_info=user_info,
            commission_name=commission_name,
            preview_text=preview_text,
            status_display=status_display
        )

        # Отправляем сообщение с клавиатурой
        await message.answer(
            response,
            reply_markup=get_appeal_keyboard(
                appeal.id,
                appeal.status,
                show_full_text=show_full_text,
                text_length=len(full_text),
                has_file=bool(appeal.file_path)  # Проверяем наличие файла
            ),
            parse_mode='HTML'  # Включаем HTML-парсинг
        )

    except Appeal.DoesNotExist:
        await message.answer(
            "🔍 <b>Обращение с таким ID не найдено.</b>",
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Произошла ошибка при обработке запроса: {e}")
        await message.answer(
            "❌ <b>Произошла ошибка.</b>\n\n"
            "<i>Пожалуйста, попробуйте позже.</i>",
            parse_mode='HTML'
        )
    finally:
        await state.clear()

# Обработка просмотра файла
@router.callback_query(F.data.startswith("appeal_view_file_"))
async def view_file(callback: CallbackQuery):
    appeal_id = int(callback.data.split("_")[3])  # Извлекаем ID обращения из callback_data

    try:
        # Получаем обращение
        appeal = await sync_to_async(Appeal.objects.get)(id=appeal_id)

        # Проверяем, что файл существует
        if appeal.file_path and hasattr(appeal.file_path, 'path') and os.path.exists(appeal.file_path.path):
            # Отправляем файл пользователю с эмодзи
            file = FSInputFile(appeal.file_path.path)
            await callback.message.answer_document(
                file,
                caption="📎 <b>Файл успешно загружен.</b>",
                parse_mode='HTML'
            )
        else:
            await callback.message.answer(
                "❌ <b>Файл не найден.</b>",
                parse_mode='HTML'
            )

    except Exception as e:
        logger.error(f"Ошибка при отправке файла: {e}")
        await callback.message.answer(
            "❌ <b>Произошла ошибка при отправке файла.</b>\n\n"
            "<i>Пожалуйста, попробуйте позже.</i>",
            parse_mode='HTML'
        )
    finally:
        await callback.answer()  # Убираем подсветку кнопки

# Обработка кнопки "Показать полностью"
@router.callback_query(F.data.startswith("appeal_show_full_"))
async def show_full_text(callback: CallbackQuery):
    appeal_id = int(callback.data.split("_")[3])  # Извлекаем ID обращения из callback_data

    try:
        # Получаем детали обращения
        appeal, user_info, commission_name, status_display = await get_appeal_details(appeal_id)

        # Формируем ответ с полным текстом с помощью функции format_appeal_response
        response = format_appeal_response(
            appeal=appeal,
            user_info=user_info,
            commission_name=commission_name,
            preview_text=appeal.appeal_text,  # Полный текст
            status_display=status_display
        )

        # Обновляем сообщение с полным текстом и новой клавиатурой
        await callback.message.edit_text(
            response,
            reply_markup=get_appeal_keyboard(
                appeal.id,
                appeal.status,
                show_full_text=True,
                text_length=len(appeal.appeal_text),
                has_file=bool(appeal.file_path)  # Проверяем наличие файла
            ),
            parse_mode='HTML'  # Включаем HTML-парсинг
        )

    except Exception as e:
        logger.error(f"Ошибка при показе полного текста: {e}")
        await callback.message.answer(
            "❌ <b>Произошла ошибка при обработке запроса.</b>\n\n"
            "<i>Пожалуйста, попробуйте позже.</i>",
            parse_mode='HTML'
        )
    finally:
        await callback.answer()  # Убираем подсветку кнопки

# Обработка кнопки "Свернуть"
@router.callback_query(F.data.startswith("appeal_collapse_"))
async def collapse_text(callback: CallbackQuery):
    appeal_id = int(callback.data.split("_")[2])  # Извлекаем ID обращения из callback_data

    try:
        # Получаем детали обращения
        appeal, user_info, commission_name, status_display = await get_appeal_details(appeal_id)

        # Определяем, нужно ли обрезать текст
        full_text = appeal.appeal_text
        preview_text = full_text[:PREVIEW_LENGTH] + "..." if len(full_text) > PREVIEW_LENGTH else full_text

        # Формируем ответ с обрезанным текстом с помощью функции format_appeal_response
        response = format_appeal_response(
            appeal=appeal,
            user_info=user_info,
            commission_name=commission_name,
            preview_text=preview_text,
            status_display=status_display
        )

        # Обновляем сообщение с обрезанным текстом и новой клавиатурой
        await callback.message.edit_text(
            response,
            reply_markup=get_appeal_keyboard(
                appeal.id,
                appeal.status,
                show_full_text=False,
                text_length=len(full_text),
                has_file=bool(appeal.file_path)  # Проверяем наличие файла
            ),
            parse_mode='HTML'  # Включаем HTML-парсинг
        )

    except Exception as e:
        logger.error(f"Ошибка при сворачивании текста: {e}")
        await callback.message.answer(
            "❌ <b>Произошла ошибка при обработке запроса.</b>\n\n"
            "<i>Пожалуйста, попробуйте позже.</i>",
            parse_mode='HTML'
        )
    finally:
        await callback.answer()  # Убираем подсветку кнопки

# Обработка кнопки "Принять"
@router.callback_query(F.data.startswith("appeal_accept_"))
async def accept_appeal(callback: CallbackQuery):
    """
    Обработка кнопки "Принять".
    """
    await update_appeal_status(callback, StatusChoices.PROCESSED)

# Обработка кнопки "Отклонить"
@router.callback_query(F.data.startswith("appeal_reject_"))
async def reject_appeal(callback: CallbackQuery):
    """
    Обработка кнопки "Отклонить".
    """
    await update_appeal_status(callback, StatusChoices.REJECTED)

# Обработка удаления обращения
@router.callback_query(F.data.startswith("appeal_delete_"))
async def delete_appeal(callback: CallbackQuery):
    appeal_id = int(callback.data.split("_")[2])  # Извлекаем ID обращения из callback_data

    try:
        # Удаляем обращение
        await sync_to_async(Appeal.objects.filter(id=appeal_id).delete)()

        # Отправляем сообщение об успешном удалении с эмодзи
        await callback.message.edit_text(
            f"🗑️ <b>Обращение #{appeal_id} успешно удалено.</b>",
            parse_mode='HTML'  # Включаем HTML-парсинг
        )

    except Exception as e:
        logger.error(f"Ошибка при удалении обращения: {e}")
        await callback.message.answer(
            "❌ <b>Произошла ошибка при обработке запроса.</b>\n\n"
            "<i>Пожалуйста, попробуйте позже.</i>",
            parse_mode='HTML'
        )
    finally:
        await callback.answer()  # Убираем подсветку кнопки