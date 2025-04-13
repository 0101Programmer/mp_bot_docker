from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from typing import Callable, Awaitable, Dict, Any
from ..tools.check_is_registred import get_user_by_telegram_id


class CheckUserRegisteredMiddleware(BaseMiddleware):
    """
    Middleware для проверки регистрации пользователя.
    Исключает команду /start из проверки.
    Работает как с сообщениями, так и с колбэками.
    """

    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        # Определяем, является ли событие сообщением или колбэком
        if isinstance(event, Message):
            # Проверяем, является ли сообщение командой /start
            if event.text and event.text.startswith("/start"):
                return await handler(event, data)

            telegram_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            telegram_id = event.from_user.id
        else:
            # Если тип события неизвестен, прерываем выполнение
            return

        # Проверяем регистрацию пользователя
        user = await get_user_by_telegram_id(telegram_id)

        if not user:
            # Формируем ответ в зависимости от типа события
            response = "Вы не зарегистрированы. Пожалуйста, начните с команды /start."

            if isinstance(event, Message):
                # Для сообщений удаляем клавиатуру и отправляем ответ
                await event.answer(response, reply_markup=ReplyKeyboardRemove())
            elif isinstance(event, CallbackQuery):
                # Для колбэков удаляем клавиатуру из предыдущего сообщения
                await event.message.edit_reply_markup(reply_markup=None)  # Удаляем клавиатуру
                await event.message.answer(response, reply_markup=ReplyKeyboardRemove())
                await event.answer()  # Закрываем уведомление о нажатии кнопки

            # Очищаем состояние FSM для незарегистрированных пользователей
            state: FSMContext = data.get("state")
            if state:
                await state.clear()

            return  # Прерываем дальнейшую обработку

        # Добавляем информацию о пользователе в данные
        data['user'] = user
        data['user_id'] = user.id

        # Добавляем флаг is_admin из модели пользователя
        data['is_admin'] = user.is_admin

        # Передаем управление дальше
        return await handler(event, data)