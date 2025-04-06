from aiogram import BaseMiddleware
from aiogram.types import Message
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
            # Пропускаем проверку для команды /start
            return await handler(event, data)

        # Получаем Telegram ID пользователя
        telegram_id = event.from_user.id

        # Проверяем, зарегистрирован ли пользователь
        user = await get_user_by_telegram_id(telegram_id)
        if not user:
            await event.answer("Вы не зарегистрированы. Пожалуйста, начните с команды /start.")
            return

        # Передаем пользователя в данные контекста
        data['user'] = user

        # Передаем управление дальше
        return await handler(event, data)