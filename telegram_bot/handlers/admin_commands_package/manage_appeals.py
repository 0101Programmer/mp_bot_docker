from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
import os
from ...models import Appeal

router = Router()

class AppealState(StatesGroup):
    waiting_for_id = State()

# Клавиатура для обращения
def get_appeal_keyboard(appeal_id: int, status: str, show_full_text: bool = False, text_length: int = 0, has_file: bool = False):
    builder = InlineKeyboardBuilder()

    # Если текст длинный и свёрнут, добавляем кнопку "Показать полностью"
    if text_length > 250 and not show_full_text:
        builder.button(text="Показать полностью", callback_data=f"appeal_show_full_{appeal_id}")

    # Если текст развёрнут, добавляем кнопку "Свернуть"
    elif text_length > 250 and show_full_text:
        builder.button(text="Свернуть", callback_data=f"appeal_collapse_{appeal_id}")

    # Добавляем кнопку "Посмотреть файл", если файл существует
    if has_file:
        builder.button(text="Посмотреть файл", callback_data=f"appeal_view_file_{appeal_id}")

    # Добавляем основные кнопки только если текст свёрнут или его длина <= 250
    if text_length <= 250 or not show_full_text:
        if status == "Новое":
            builder.button(text="Принять", callback_data=f"appeal_accept_{appeal_id}")
            builder.button(text="Отклонить", callback_data=f"appeal_reject_{appeal_id}")
        builder.button(text="Удалить", callback_data=f"appeal_delete_{appeal_id}")

    builder.adjust(1)  # Кнопки будут расположены по одной в строке
    return builder.as_markup()


# Обработка кнопки "Просмотр обращений"
@router.callback_query(F.data == "view_appeals")
async def view_appeals(callback: CallbackQuery, state: FSMContext):
    # Отправляем ответ на коллбэк, чтобы убрать подсветку кнопки
    await callback.answer()

    # Запрашиваем ID обращения
    await callback.message.answer("Введите ID обращения (только цифры):")
    await state.set_state(AppealState.waiting_for_id)


# Обработка ввода ID
@router.message(AppealState.waiting_for_id)
async def process_appeal_id(message: Message, state: FSMContext):
    appeal_id = message.text.strip()

    # Проверяем, что введены только цифры
    if not appeal_id.isdigit():
        await message.answer("Некорректный ввод. Введите только цифры:")
        return

    try:
        # Получаем обращение с использованием select_related
        appeal = await sync_to_async(Appeal.objects.select_related('user', 'commission').get)(id=int(appeal_id))

        # Получаем данные пользователя через sync_to_async
        user_info = await sync_to_async(lambda: appeal.user.username if appeal.user else "Неизвестен")()

        # Получаем название комиссии через sync_to_async
        commission_name = await sync_to_async(lambda: appeal.commission.name if appeal.commission else "Комиссия не указана")()

        # Определяем, нужно ли обрезать текст
        if len(appeal.appeal_text) > 250:
            truncated_text = appeal.appeal_text[:100] + "..."
            response = (
                f"Обращение #{appeal.id}\n"
                f"Пользователь: {user_info}\n"
                f"Комиссия: {commission_name}\n"
                f"Текст обращения: {truncated_text}\n"
                f"Контактная информация: {appeal.contact_info or 'Не указана'}\n"
                f"Статус: {appeal.status}"
            )
            await message.answer(
                response,
                reply_markup=get_appeal_keyboard(
                    appeal.id,
                    appeal.status,
                    show_full_text=False,
                    text_length=len(appeal.appeal_text),
                    has_file=bool(appeal.file_path)  # Проверяем наличие файла
                )
            )
        else:
            response = (
                f"Обращение #{appeal.id}\n"
                f"Пользователь: {user_info}\n"
                f"Комиссия: {commission_name}\n"
                f"Текст обращения: {appeal.appeal_text}\n"
                f"Контактная информация: {appeal.contact_info or 'Не указана'}\n"
                f"Статус: {appeal.status}"
            )
            await message.answer(
                response,
                reply_markup=get_appeal_keyboard(
                    appeal.id,
                    appeal.status,
                    show_full_text=True,
                    text_length=len(appeal.appeal_text),
                    has_file=bool(appeal.file_path)  # Проверяем наличие файла
                )
            )

    except Appeal.DoesNotExist:
        await message.answer("Обращение с таким ID не найдено.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        await message.answer("Произошла ошибка при обработке запроса.")
    finally:
        await state.clear()

@router.callback_query(F.data.startswith("appeal_view_file_"))
async def view_file(callback: CallbackQuery):
    appeal_id = int(callback.data.split("_")[3])  # Извлекаем ID обращения из callback_data

    try:
        # Получаем обращение
        appeal = await sync_to_async(Appeal.objects.get)(id=appeal_id)

        # Проверяем, что файл существует
        if appeal.file_path and os.path.exists(appeal.file_path):
            # Отправляем файл пользователю
            file = FSInputFile(appeal.file_path)
            await callback.message.answer_document(file)
        else:
            await callback.message.answer("Файл не найден.")

    except Exception as e:
        print(f"Ошибка при отправке файла: {e}")
        await callback.message.answer("Произошла ошибка при отправке файла.")
    finally:
        await callback.answer()  # Убираем подсветку кнопки

# Обработка кнопки "Показать полностью"
@router.callback_query(F.data.startswith("appeal_show_full_"))
async def show_full_text(callback: CallbackQuery):
    appeal_id = int(callback.data.split("_")[3])  # Извлекаем ID обращения из callback_data

    try:
        # Получаем обращение с использованием select_related
        appeal = await sync_to_async(Appeal.objects.select_related('user', 'commission').get)(id=appeal_id)

        # Получаем данные пользователя через sync_to_async
        user_info = await sync_to_async(lambda: appeal.user.username if appeal.user else "Неизвестен")()

        # Получаем название комиссии через sync_to_async
        commission_name = await sync_to_async(lambda: appeal.commission.name if appeal.commission else "Комиссия не указана")()

        # Формируем ответ с полным текстом
        response = (
            f"Обращение #{appeal.id}\n"
            f"Пользователь: {user_info}\n"
            f"Комиссия: {commission_name}\n"
            f"Текст обращения: {appeal.appeal_text}\n"
            f"Контактная информация: {appeal.contact_info or 'Не указана'}\n"
            f"Статус: {appeal.status}"
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
            )
        )

    except Exception as e:
        print(f"Ошибка при показе полного текста: {e}")
        await callback.message.answer("Произошла ошибка при обработке запроса.")
    finally:
        await callback.answer()  # Убираем подсветку кнопки

# Обработка кнопки "Свернуть"
@router.callback_query(F.data.startswith("appeal_collapse_"))
async def collapse_text(callback: CallbackQuery):
    appeal_id = int(callback.data.split("_")[2])  # Извлекаем ID обращения из callback_data

    try:
        # Получаем обращение с использованием select_related
        appeal = await sync_to_async(Appeal.objects.select_related('user', 'commission').get)(id=appeal_id)

        # Получаем данные пользователя через sync_to_async
        user_info = await sync_to_async(lambda: appeal.user.username if appeal.user else "Неизвестен")()

        # Получаем название комиссии через sync_to_async
        commission_name = await sync_to_async(lambda: appeal.commission.name if appeal.commission else "Комиссия не указана")()

        # Определяем, нужно ли обрезать текст
        truncated_text = appeal.appeal_text[:100] + "..." if len(appeal.appeal_text) > 250 else appeal.appeal_text
        response = (
            f"Обращение #{appeal.id}\n"
            f"Пользователь: {user_info}\n"
            f"Комиссия: {commission_name}\n"
            f"Текст обращения: {truncated_text}\n"
            f"Контактная информация: {appeal.contact_info or 'Не указана'}\n"
            f"Статус: {appeal.status}"
        )

        # Обновляем сообщение с обрезанным текстом и новой клавиатурой
        await callback.message.edit_text(
            response,
            reply_markup=get_appeal_keyboard(
                appeal.id,
                appeal.status,
                show_full_text=False,
                text_length=len(appeal.appeal_text),
                has_file=bool(appeal.file_path)  # Проверяем наличие файла
            )
        )

    except Exception as e:
        print(f"Ошибка при сворачивании текста: {e}")
        await callback.message.answer("Произошла ошибка при обработке запроса.")
    finally:
        await callback.answer()  # Убираем подсветку кнопки

# Обработка принятия обращения
@router.callback_query(F.data.startswith("appeal_accept_"))
async def accept_appeal(callback: CallbackQuery):
    appeal_id = int(callback.data.split("_")[2])  # Извлекаем ID обращения из callback_data

    try:
        # Обновляем статус обращения на "Обработана"
        await sync_to_async(Appeal.objects.filter(id=appeal_id).update)(status="Обработано")

        # Получаем обновленное обращение
        appeal = await sync_to_async(Appeal.objects.get)(id=appeal_id)

        # Обновляем сообщение с новым статусом и клавиатурой
        response = (
            f"Обращение #{appeal.id}\n"
            f"Статус: {appeal.status}"
        )
        await callback.message.edit_text(
            response,
            reply_markup=get_appeal_keyboard(appeal.id, appeal.status)
        )
    except Exception as e:
        print(f"Ошибка при принятии обращения: {e}")
        await callback.message.answer("Произошла ошибка при обработке запроса.")
    finally:
        await callback.answer()  # Убираем подсветку кнопки

# Обработка отклонения обращения
@router.callback_query(F.data.startswith("appeal_reject_"))
async def reject_appeal(callback: CallbackQuery):
    appeal_id = int(callback.data.split("_")[2])  # Извлекаем ID обращения из callback_data

    try:
        # Обновляем статус обращения на "Отклонена"
        await sync_to_async(Appeal.objects.filter(id=appeal_id).update)(status="Отклонено")

        # Получаем обновленное обращение
        appeal = await sync_to_async(Appeal.objects.get)(id=appeal_id)

        # Обновляем сообщение с новым статусом и клавиатурой
        response = (
            f"Обращение #{appeal.id}\n"
            f"Статус: {appeal.status}"
        )
        await callback.message.edit_text(
            response,
            reply_markup=get_appeal_keyboard(appeal.id, appeal.status)
        )
    except Exception as e:
        print(f"Ошибка при отклонении обращения: {e}")
        await callback.message.answer("Произошла ошибка при обработке запроса.")
    finally:
        await callback.answer()  # Убираем подсветку кнопки

# Обработка удаления обращения
@router.callback_query(F.data.startswith("appeal_delete_"))
async def delete_appeal(callback: CallbackQuery):
    appeal_id = int(callback.data.split("_")[2])
    try:
        await sync_to_async(Appeal.objects.filter(id=appeal_id).delete)()
        await callback.message.edit_text(f"Обращение #{appeal_id} успешно удалено.")
    except Exception as e:
        print(f"Ошибка при удалении обращения: {e}")
        await callback.message.answer("Произошла ошибка при обработке запроса.")
    finally:
        await callback.answer()