from aiogram import BaseMiddleware
from aiogram.types import Message, ReplyKeyboardRemove  # Добавляем импорт
from typing import Callable, Awaitable, Dict, Any
from ..tools.check_is_registred import get_user_by_telegram_id


class CheckUserRegisteredMiddleware(BaseMiddleware):
    """
    Middleware для проверки регистрации пользователя.
    Исключает команду /start из проверки.
    """

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        # Проверяем, является ли сообщение командой /start
        if event.text and event.text.startswith("/start"):
            return await handler(event, data)

        telegram_id = event.from_user.id
        user = await get_user_by_telegram_id(telegram_id)

        if not user:
            # Отправляем сообщение и удаляем reply-клавиатуру
            await event.answer(
                "Вы не зарегистрированы. Пожалуйста, начните с команды /start.",
                reply_markup=ReplyKeyboardRemove()  # Удаляем клавиатуру
            )
            return  # Прерываем дальнейшую обработку

        data['user'] = user
        return await handler(event, data)