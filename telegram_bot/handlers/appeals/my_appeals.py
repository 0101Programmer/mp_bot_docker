
from aiogram import Router, F
from aiogram.types import FSInputFile, InlineKeyboardButton
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from ...models import Appeal
from ...tools.main_logger import logger

router = Router()

# Кастомизированные эмодзи для статусов
STATUS_EMOJIS = {
    'новое': '🆕',
    'обработано': '✅',
    'отклонено': '❌'
}

# Словарь для красивого отображения статусов
STATUS_DISPLAY_NAMES = {
    'новое': 'Новое',
    'обработано': 'Обработано',
    'отклонено': 'Отклонено'
}


async def generate_appeal_response(appeal: Appeal) -> tuple[str, InlineKeyboardBuilder]:
    """
    Генерирует текст ответа и клавиатуру для обращения.
    Возвращает кортеж (текст, клавиатура)
    """
    # Нормализуем статус
    status_lower = appeal.status.lower()
    status_display = STATUS_DISPLAY_NAMES.get(status_lower, appeal.status)
    status_emoji = STATUS_EMOJIS.get(status_lower, '📄')

    # Получаем название комиссии
    commission_name = appeal.commission.name if appeal.commission else "Не указана"

    # Определяем, нужно ли обрезать текст
    preview_length = 300  # Количество символов для предпросмотра
    needs_expansion = len(appeal.appeal_text) > preview_length
    display_text = appeal.appeal_text[:preview_length] + "..." if needs_expansion else appeal.appeal_text

    # Форматируем даты
    created_at_formatted = appeal.created_at.strftime("%d.%m.%Y %H:%M")
    updated_at_formatted = appeal.updated_at.strftime("%d.%m.%Y %H:%M")

    # Формируем текст
    response = (
        f"📌 Обращение №{appeal.id}\n"
        f"{status_emoji} Статус: {status_display}\n"
        f"👥 Комиссия: {commission_name}\n"
        f"📝 Текст: {display_text}\n"
        f"📞 Контактная информация: {appeal.contact_info or 'Не указана'}\n"
        f"📅 Дата создания: {created_at_formatted}\n"
        f"🔄 Последнее обновление: {updated_at_formatted}"
    )

    # Создаем клавиатуру
    builder = InlineKeyboardBuilder()

    # Добавляем кнопку "Показать полностью" только если текст обрезан
    if needs_expansion:
        builder.button(text="📄 Показать полностью", callback_data=f"show_full:{appeal.id}")

    # Кнопка "Удалить"
    builder.button(text="🗑 Удалить", callback_data=f"delete_appeal:{appeal.id}")

    # Кнопка "Открыть файл", если файл прикреплен
    if appeal.file_path:
        builder.button(text="📎 Открыть файл", callback_data=f"view_file:{appeal.id}")

    # Настройка расположения кнопок
    builder.adjust(1)

    return response, builder


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
            # Нормализуем статус (на случай разных регистров)
            status_lower = appeal.status.lower()

            # Получаем эмодзи и отображаемое имя статуса
            status_emoji = STATUS_EMOJIS.get(status_lower, '📄')
            status_display = STATUS_DISPLAY_NAMES.get(status_lower, appeal.status)

            # Получаем название комиссии
            commission_name = appeal.commission.name if appeal.commission else "Без комиссии"

            # Формируем текст кнопки
            button_text = (
                f"№{appeal.id} | {status_emoji} {status_display} | "
                f"{commission_name}"
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

        await callback.message.answer(response, reply_markup=builder.as_markup())
        await callback.answer()

    except Appeal.DoesNotExist:
        await callback.answer("❌ Обращение не найдено!", show_alert=True)
    except Exception as e:
        logger.error(f"Error in show_appeal_detail: {e}")
        await callback.answer("⚠️ Произошла ошибка!", show_alert=True)


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

        # Получаем сокращенную версию сообщения
        short_response, builder = await generate_appeal_response(appeal)

        # Формируем полную версию
        status_emoji = STATUS_EMOJIS.get(appeal.status.lower(), '📄')
        status_display = STATUS_DISPLAY_NAMES.get(appeal.status.lower(), appeal.status)
        commission_name = appeal.commission.name if appeal.commission else "Не указана"

        full_response = (
            f"📌 Обращение №{appeal_id}\n"
            f"{status_emoji} Статус: {status_display}\n"
            f"👥 Комиссия: {commission_name}\n\n"
            f"📝 Полный текст:\n\n"
            f"{appeal.appeal_text}\n"
        )

        if appeal.file_path:
            full_response += "\n📎 Прикреплён документ"

        # Создаем кнопки для полной версии
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

        # Если это ответ на существующее сообщение - редактируем его
        if callback.message:
            await callback.message.edit_text(
                full_response,
                reply_markup=full_builder.as_markup()
            )
        else:
            await callback.message.answer(
                full_response,
                reply_markup=full_builder.as_markup()
            )

        await callback.answer()

    except Appeal.DoesNotExist:
        await callback.answer("❌ Обращение не найдено", show_alert=True)
    except Exception as e:
        logger.error(f"Error in show_full_appeal: {e}", exc_info=True)
        await callback.answer("⚠️ Ошибка при загрузке", show_alert=True)


@router.callback_query(F.data.startswith("collapse:"))
async def collapse_appeal(callback: CallbackQuery):
    try:
        appeal_id = int(callback.data.split(":")[1])
        appeal = await sync_to_async(
            Appeal.objects.select_related('commission').get
        )(id=appeal_id)

        # Получаем сокращенную версию
        response, builder = await generate_appeal_response(appeal)

        # Редактируем сообщение обратно
        await callback.message.edit_text(
            response,
            reply_markup=builder.as_markup()
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in collapse_appeal: {e}")
        await callback.answer("⚠️ Ошибка при сворачивании", show_alert=True)


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

        # Удаляем файл если он есть
        if appeal.file_path:
            try:
                await sync_to_async(appeal.file_path.storage.delete)(appeal.file_path.name)
            except Exception as e:
                logger.error(f"File delete error: {e}")

        # Удаляем запись
        await sync_to_async(appeal.delete)()

        # Обновляем сообщение
        await callback.message.edit_text(
            "✅ Обращение успешно удалено",
            reply_markup=None  # Убираем все кнопки
        )
        await callback.answer()

    except Appeal.DoesNotExist:
        await callback.message.edit_text("❌ Обращение не найдено")
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in confirm_delete: {e}", exc_info=True)
        await callback.message.edit_text("⚠️ Ошибка при удалении")
        await callback.answer()


# Обработчик отмены удаления
@router.callback_query(F.data.startswith("cancel_delete:"))
async def cancel_delete_appeal(callback: CallbackQuery):
    try:
        appeal_id = int(callback.data.split(":")[1])

        # Получаем полные данные обращения
        appeal = await sync_to_async(
            Appeal.objects.select_related('commission').get
        )(id=appeal_id)

        # Генерируем стандартный ответ
        response, builder = await generate_appeal_response(appeal)

        # Обновляем сообщение
        await callback.message.edit_text(
            response,
            reply_markup=builder.as_markup()
        )
        await callback.answer("❌ Удаление отменено")

    except Appeal.DoesNotExist:
        await callback.answer("❌ Обращение не найдено", show_alert=True)
    except Exception as e:
        logger.error(f"Error in cancel_delete: {e}", exc_info=True)
        await callback.answer("⚠️ Ошибка при отмене", show_alert=True)
