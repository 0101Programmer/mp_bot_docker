from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from ...models import Appeal

router = Router()

class AppealState(StatesGroup):
    waiting_for_id = State()

# Клавиатура для обращения
def get_appeal_keyboard(appeal_id: int, status: str):
    builder = InlineKeyboardBuilder()

    # Если статус "Новое", добавляем кнопки "Принять" и "Отклонить"
    if status == "Новое":
        builder.button(text="Принять", callback_data=f"appeal_accept_{appeal_id}")
        builder.button(text="Отклонить", callback_data=f"appeal_reject_{appeal_id}")

    # Кнопка "Удалить" доступна всегда
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
        appeal = await sync_to_async(Appeal.objects.select_related('user').get)(id=int(appeal_id))

        # Получаем данные пользователя через sync_to_async
        user_info = await sync_to_async(lambda: appeal.user.username if appeal.user else "Неизвестен")()

        # Формируем ответ
        response = (
            f"Обращение #{appeal.id}\n"
            f"Пользователь: {user_info}\n"
            f"Текст обращения: {appeal.appeal_text}\n"
            f"Контактная информация: {appeal.contact_info or 'Не указана'}\n"
            f"Статус: {appeal.status}"
        )

        # Отправляем сообщение с клавиатурой, зависящей от статуса
        await message.answer(response, reply_markup=get_appeal_keyboard(appeal.id, appeal.status))

    except Appeal.DoesNotExist:
        await message.answer("Обращение с таким ID не найдено.")
    except Exception as e:
        # Логируем ошибку для отладки
        print(f"Произошла ошибка: {e}")
        await message.answer("Произошла ошибка при обработке запроса.")
    finally:
        # Сбрасываем состояние
        await state.clear()

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