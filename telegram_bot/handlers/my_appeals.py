from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from asgiref.sync import sync_to_async
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os
from ..models import User, Appeal  # Импортируем модели User и Appeal
import logging  # Импортируем модуль logging
from aiogram.types import FSInputFile

# Настройка логгера
logger = logging.getLogger(__name__)  # Создаем логгер для текущего модуля

router = Router()

# Обработчик для кнопки "Отследить статус обращения"
@router.message(F.text == "Отследить статус обращения")
async def track_appeal_status(message: Message):
    # Получаем Telegram ID пользователя
    telegram_id = message.from_user.id

    try:
        # Находим пользователя в базе данных
        user = await sync_to_async(User.objects.get)(telegram_id=telegram_id)

        # Находим все обращения пользователя
        appeals = await sync_to_async(list)(Appeal.objects.filter(user=user).select_related('commission'))

        if appeals:
            # Отправляем первое сообщение
            await message.answer("Ваши обращения:")

            # Отправляем каждое обращение отдельным сообщением
            for appeal in appeals:
                # Ограничиваем длину текста для предварительного просмотра
                preview_text = appeal.appeal_text[:100] + "..." if len(appeal.appeal_text) > 250 else appeal.appeal_text

                # Получаем название комиссии через sync_to_async
                commission_name = await sync_to_async(lambda: appeal.commission.name if appeal.commission else "Комиссия не указана")()

                # Проверяем наличие прикрепленного файла или фото
                file_info = ""
                if appeal.file_path:
                    if "_file_" in appeal.file_path:
                        file_info = "Есть прикрепленный документ.\n"
                    elif "_photo_" in appeal.file_path:
                        file_info = "Есть прикрепленное фото.\n"

                response = (
                    f"Обращение: {preview_text}\n"
                    f"Статус: {appeal.status}\n"
                    f"Комиссия: {commission_name}\n"
                    f"{file_info}"  # Добавляем информацию о файле, если есть
                )

                # Создаем inline-клавиатуру с кнопками
                builder = InlineKeyboardBuilder()
                if len(appeal.appeal_text) > 250:
                    builder.button(text="Показать полностью", callback_data=f"show_full:{appeal.id}")
                builder.button(text="Удалить", callback_data=f"delete_appeal:{appeal.id}")

                # Если есть файл, добавляем кнопку для просмотра
                if appeal.file_path:
                    builder.button(text="Посмотреть файл", callback_data=f"view_file:{appeal.id}")

                builder.adjust(1)  # Кнопки в одну строку

                # Отправляем сообщение с inline-кнопками
                await message.answer(response, reply_markup=builder.as_markup())
        else:
            await message.answer("У вас пока нет обращений.")

    except User.DoesNotExist:
        await message.answer("Вы не зарегистрированы. Пожалуйста, начните с команды /start.")
    except Exception as e:
        # Логируем ошибку
        logger.error(f"Ошибка при отслеживании статусов обращений: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик для кнопки "Посмотреть файл"
@router.callback_query(F.data.startswith("view_file:"))
async def view_file(callback_query: CallbackQuery):
    try:
        # Извлекаем ID обращения из callback_data
        appeal_id = int(callback_query.data.split(":")[1])

        # Находим обращение в базе данных
        appeal = await sync_to_async(Appeal.objects.get)(id=appeal_id)

        # Проверяем, существует ли файл
        if appeal.file_path and os.path.exists(appeal.file_path):
            # Отправляем файл пользователю
            file = FSInputFile(appeal.file_path)
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
@router.callback_query(lambda query: query.data.startswith("show_full"))
async def show_full_appeal(callback):
    try:
        # Извлекаем ID обращения из callback_data
        appeal_id = int(callback.data.split(":")[1])

        # Находим обращение в базе данных с использованием select_related
        appeal = await sync_to_async(Appeal.objects.select_related('commission').get)(id=appeal_id)

        # Получаем название комиссии через sync_to_async
        commission_name = await sync_to_async(
            lambda: appeal.commission.name if appeal.commission else "Комиссия не указана"
        )()

        # Проверяем наличие прикрепленного файла или фото
        file_info = ""
        if appeal.file_path:
            if "_file_" in appeal.file_path:
                file_info = "Есть прикрепленный документ.\n"
            elif "_photo_" in appeal.file_path:
                file_info = "Есть прикрепленное фото.\n"

        # Формируем ответ с полным текстом обращения
        full_response = (
            f"Полный текст обращения:\n\n"
            f"{appeal.appeal_text}\n\n"
            f"Статус: {appeal.status}\n"
            f"Комиссия: {commission_name}\n"
            f"{file_info}"  # Добавляем информацию о файле, если есть
        )

        # Создаем inline-клавиатуру с кнопкой "Свернуть"
        builder = InlineKeyboardBuilder()
        builder.button(text="Свернуть", callback_data=f"collapse:{appeal.id}")

        # Если есть файл, добавляем кнопку для просмотра
        if appeal.file_path:
            builder.button(text="Посмотреть файл", callback_data=f"view_file:{appeal.id}")

        builder.adjust(1)  # Кнопки в одну строку

        # Редактируем текущее сообщение, заменяя его на полный текст и добавляя кнопку "Свернуть"
        await callback.message.edit_text(full_response, reply_markup=builder.as_markup())

        # Убираем часы загрузки (подтверждаем выполнение callback)
        await callback.answer()

    except Appeal.DoesNotExist:
        await callback.answer("Обращение не найдено.", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка при показе полного текста обращения: {e}")
        await callback.answer("Произошла ошибка. Пожалуйста, попробуйте позже.", show_alert=True)


# Обработчик нажатия на кнопку "Свернуть"
@router.callback_query(lambda query: query.data.startswith("collapse"))
async def collapse_appeal(callback: CallbackQuery):
    try:
        # Извлекаем ID обращения из callback_data
        appeal_id = int(callback.data.split(":")[1])

        # Находим обращение в базе данных с использованием select_related
        appeal = await sync_to_async(Appeal.objects.select_related('commission').get)(id=appeal_id)

        # Ограничиваем длину текста для предварительного просмотра
        preview_text = appeal.appeal_text[:100] + "..." if len(appeal.appeal_text) > 250 else appeal.appeal_text

        # Получаем название комиссии через sync_to_async
        commission_name = await sync_to_async(
            lambda: appeal.commission.name if appeal.commission else "Комиссия не указана"
        )()

        # Проверяем наличие прикрепленного файла или фото
        file_info = ""
        if appeal.file_path:
            if "_file_" in appeal.file_path:
                file_info = "Есть прикрепленный документ.\n"
            elif "_photo_" in appeal.file_path:
                file_info = "Есть прикрепленное фото.\n"

        # Формируем ответ с сокращённым текстом
        collapsed_response = (
            f"Обращение: {preview_text}\n"
            f"Статус: {appeal.status}\n"
            f"Комиссия: {commission_name}\n"
            f"{file_info}"  # Добавляем информацию о файле, если есть
        )

        # Создаем inline-клавиатуру с кнопками
        builder = InlineKeyboardBuilder()
        if len(appeal.appeal_text) > 250:
            builder.button(text="Показать полностью", callback_data=f"show_full:{appeal.id}")
        builder.button(text="Удалить", callback_data=f"delete_appeal:{appeal.id}")

        # Если есть файл, добавляем кнопку для просмотра
        if appeal.file_path:
            builder.button(text="Посмотреть файл", callback_data=f"view_file:{appeal.id}")

        builder.adjust(1)  # Кнопки в одну строку

        # Редактируем текущее сообщение, возвращая его к сокращённому виду
        await callback.message.edit_text(collapsed_response, reply_markup=builder.as_markup())

        # Убираем часы загрузки (подтверждаем выполнение callback)
        await callback.answer()

    except Appeal.DoesNotExist:
        await callback.answer("Обращение не найдено.", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка при сворачивании текста обращения: {e}")
        await callback.answer("Произошла ошибка. Пожалуйста, попробуйте позже.", show_alert=True)

# Обработчик нажатия на кнопку "Удалить"
@router.callback_query(F.data.startswith("delete_appeal:"))
async def confirm_delete_appeal(callback_query):
    try:
        # Извлекаем ID обращения из callback_data
        appeal_id = int(callback_query.data.split(":")[1])

        # Создаем inline-клавиатуру с кнопками "Да" и "Нет"
        builder = InlineKeyboardBuilder()
        builder.button(text="Да", callback_data=f"confirm_delete:{appeal_id}")
        builder.button(text="Нет", callback_data=f"cancel_delete:{appeal_id}")
        builder.adjust(2)

        # Отправляем сообщение с запросом подтверждения
        await callback_query.message.edit_text(
            "Удаление обращения очистит всю его историю, а также отзовёт его, "
            "в случае, если оно не было обработано. Вы уверены?",
            reply_markup=builder.as_markup()
        )

    except Exception as e:
        logger.error(f"Ошибка при запросе подтверждения удаления: {e}")
        await callback_query.message.edit_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик подтверждения удаления
@router.callback_query(F.data.startswith("confirm_delete:"))
async def delete_appeal(callback_query):
    try:
        # Извлекаем ID обращения из callback_data
        appeal_id = int(callback_query.data.split(":")[1])

        # Находим обращение в базе данных
        appeal = await sync_to_async(Appeal.objects.get)(id=appeal_id)

        # Проверяем, есть ли прикреплённый файл
        if appeal.file_path and os.path.exists(appeal.file_path):
            try:
                # Удаляем файл с диска
                os.remove(appeal.file_path)
            except Exception as e:
                logger.error(f"Ошибка при удалении файла {appeal.file_path}: {e}")

        # Удаляем обращение из базы данных
        await sync_to_async(Appeal.objects.filter(id=appeal_id).delete)()

        # Отправляем сообщение об успешном удалении
        await callback_query.message.edit_text("Обращение успешно удалено.")

    except Appeal.DoesNotExist:
        await callback_query.message.edit_text("Обращение не найдено.")
    except Exception as e:
        logger.error(f"Ошибка при удалении обращения: {e}")
        await callback_query.message.edit_text("Произошла ошибка. Пожалуйста, попробуйте позже.")

# Обработчик отмены удаления
@router.callback_query(F.data.startswith("cancel_delete:"))
async def cancel_delete_appeal(callback_query: CallbackQuery):
    try:
        # Извлекаем ID обращения из callback_data
        appeal_id = int(callback_query.data.split(":")[1])

        # Находим обращение в базе данных с использованием select_related
        appeal = await sync_to_async(Appeal.objects.select_related('commission').get)(id=appeal_id)

        # Получаем название комиссии через sync_to_async
        commission_name = await sync_to_async(
            lambda: appeal.commission.name if appeal.commission else "Комиссия не указана"
        )()

        # Проверяем наличие прикрепленного файла или фото
        file_info = ""
        if appeal.file_path:
            if "_file_" in appeal.file_path:
                file_info = "Есть прикрепленный документ.\n"
            elif "_photo_" in appeal.file_path:
                file_info = "Есть прикрепленное фото.\n"

        # Ограничиваем длину текста для предварительного просмотра
        preview_text = appeal.appeal_text[:100] + "..." if len(appeal.appeal_text) > 250 else appeal.appeal_text

        # Формируем текст сообщения
        response = (
            f"Обращение: {preview_text}\n"
            f"Статус: {appeal.status}\n"
            f"Комиссия: {commission_name}\n"
            f"{file_info}"  # Добавляем информацию о файле, если есть
        )

        # Создаем inline-клавиатуру с кнопками
        builder = InlineKeyboardBuilder()
        if len(appeal.appeal_text) > 250:
            builder.button(text="Показать полностью", callback_data=f"show_full:{appeal.id}")
        builder.button(text="Удалить", callback_data=f"delete_appeal:{appeal.id}")

        # Если есть файл, добавляем кнопку для просмотра
        if appeal.file_path:
            builder.button(text="Посмотреть файл", callback_data=f"view_file:{appeal.id}")

        builder.adjust(1)  # Кнопки в одну колонку (вертикальное расположение)

        # Редактируем текущее сообщение, добавляя все кнопки
        await callback_query.message.edit_text(response, reply_markup=builder.as_markup())

        # Убираем часы загрузки (подтверждаем выполнение callback)
        await callback_query.answer()

    except Appeal.DoesNotExist:
        await callback_query.answer("Обращение не найдено.", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка при отмене удаления: {e}")
        await callback_query.answer("Произошла ошибка. Пожалуйста, попробуйте позже.", show_alert=True)