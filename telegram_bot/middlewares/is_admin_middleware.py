from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Dict, Any

from aiogram.fsm.context import FSMContext

from ..tools.main_logger import logger
from ..tools.check_admin_requests import check_admin_requests
from ..tools.check_admin_status import is_user_admin


from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove


# class CheckAdminMiddleware(BaseMiddleware):
#     """
#     Middleware для строгой проверки статуса администратора.
#     Полностью блокирует выполнение для неадминов.
#     """
#
#     async def __call__(
#             self,
#             handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
#             event: Message | CallbackQuery,
#             data: Dict[str, Any]
#     ) -> Any:
#         # Проверяем, что данные о пользователе есть (должны быть добавлены предыдущим мидлвейром)
#         if 'user' not in data or 'is_admin' not in data:
#             logger.error("Critical: 'user' or 'is_admin' missing in data!")
#             return await handler(event, data)
#
#         user = data['user']
#         is_admin = data['is_admin']
#
#         print(f"User {user.username} is admin: {is_admin}")  # Логируем для отладки
#
#         # Жёсткая блокировка для неадминов
#         if not is_admin:
#             response = "У вас нет прав администратора!"
#             if isinstance(event, Message):
#                 await event.answer(response, reply_markup=ReplyKeyboardRemove())
#             elif isinstance(event, CallbackQuery):
#                 await event.message.answer(response, reply_markup=ReplyKeyboardRemove())
#                 await event.answer()  # Закрываем всплывающее уведомление
#             return  # Полностью прерываем цепочку обработки
#
#         # Если пользователь админ — пропускаем дальше
#         return await handler(event, data)


# class CheckAdminMiddleware(BaseMiddleware):
#     """
#     Middleware для проверки статуса администратора.
#     Для неадминов показывает статус заявки или предлагает подать новую.
#     """
#
#     async def __call__(
#             self,
#             handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
#             event: Message | CallbackQuery,
#             data: Dict[str, Any]
#     ) -> Any:
#         # Проверяем наличие обязательных данных
#         if 'user' not in data:
#             logger.error("User data missing in middleware!")
#             return await handler(event, data)
#
#         user = data['user']
#         is_admin = data.get('is_admin')
#
#         # Если пользователь админ - пропускаем
#         if is_admin:
#             return await handler(event, data)
#
#         # Получаем информацию о заявках пользователя
#         response, reply_markup, allow_submit = await check_admin_requests(user)
#
#         # Отправляем соответствующий ответ
#         if isinstance(event, Message):
#             await event.answer(response, reply_markup=reply_markup)
#         elif isinstance(event, CallbackQuery):
#             await event.message.answer(response, reply_markup=reply_markup)
#             await event.answer()  # Закрываем всплывающее уведомление
#
#         return  # Прерываем выполнение для неадминов

class CheckAdminMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        if 'user' not in data:
            logger.error("User data missing!")
            return await handler(event, data)

        user = data['user']
        state: FSMContext = data.get('state')

        if not state:
            return await handler(event, data)

        is_admin = data.get('is_admin', False)

        if is_admin:
            return await handler(event, data)

        response, reply_markup, allow_submit = await check_admin_requests(user)

        # Сохраняем данные в state
        await state.update_data(
            admin_request={
                'response': response,
                'reply_markup': reply_markup,
                'allow_submit': allow_submit
            }
        )

        if isinstance(event, CallbackQuery) and event.data == "submit_admin_request":
            return await handler(event, data)

        if isinstance(event, Message):
            await event.answer(response, reply_markup=reply_markup)
        elif isinstance(event, CallbackQuery):
            await event.message.answer(response, reply_markup=reply_markup)
            await event.answer()

        return