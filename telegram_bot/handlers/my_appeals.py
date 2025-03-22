from aiogram.types import Message
from aiogram import Router
from asgiref.sync import sync_to_async
from ..models import User, Appeal  # Импортируем модели User и Appeal
import logging  # Импортируем модуль logging

# Настройка логгера
logger = logging.getLogger(__name__)  # Создаем логгер для текущего модуля

router = Router()

# Обработчик текста "Отследить статус обращения"
@router.message(lambda message: message.text == "Отследить статус обращения")
async def track_appeal_status(message: Message):
    # Получаем Telegram ID пользователя
    telegram_id = message.from_user.id

    try:
        # Находим пользователя в базе данных
        user = await sync_to_async(User.objects.get)(telegram_id=telegram_id)

        # Находим все обращения пользователя
        appeals = await sync_to_async(list)(Appeal.objects.filter(user=user))

        if appeals:
            # Отправляем первое сообщение
            await message.answer("Ваши обращения:")

            # Отправляем каждое обращение отдельным сообщением
            for appeal in appeals:
                response = (
                    f"Обращение: {appeal.appeal_text[:100]}...\n"  # Ограничиваем длину текста
                    f"Статус: {appeal.status}\n"
                )
                await message.answer(response)
        else:
            await message.answer("У вас пока нет обращений.")

    except User.DoesNotExist:
        await message.answer("Вы не зарегистрированы. Пожалуйста, начните с команды /start.")
    except Exception as e:
        # Логируем ошибку
        logger.error(f"Ошибка при отслеживании статусов обращений: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")