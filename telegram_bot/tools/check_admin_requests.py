from ..models import User, AdminRequest
from asgiref.sync import sync_to_async
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def check_admin_requests(user: User):
    """
    Проверяет статус заявок пользователя на административные права.
    Возвращает кортеж (response_message, reply_markup) или None, если заявок нет.
    """
    # Проверяем, есть ли у пользователя заявка в ожидании
    pending_request_exists = await sync_to_async(AdminRequest.objects.filter(user=user, status='pending').exists)()
    if pending_request_exists:
        return (
            "Ваша заявка на административные права находится на рассмотрении. Пожалуйста, ожидайте.",
            None
        )

    # Проверяем, есть ли отклонённая заявка
    rejected_request_exists = await sync_to_async(
        AdminRequest.objects.filter(user=user, status='rejected').exists
    )()
    if rejected_request_exists:
        # Получаем последнюю отклонённую заявку
        rejected_request = await sync_to_async(
            AdminRequest.objects.filter(user=user, status='rejected').last
        )()

        # Формируем сообщение с комментарием
        response = (
            f"Ваша предыдущая заявка на административные права была отклонена.\n"
            f"Комментарий: {rejected_request.comment}\n"
            f"Вы можете подать новую заявку."
        )

        # Создаем кнопку для подачи новой заявки
        builder = InlineKeyboardBuilder()
        builder.button(text="Подать заявку", callback_data="submit_admin_request")
        builder.adjust(1)

        return response, builder.as_markup()

    # Если заявок нет, предлагаем подать новую
    builder = InlineKeyboardBuilder()
    builder.button(text="Подать заявку", callback_data="submit_admin_request")
    builder.adjust(1)

    return "У вас нет статуса администратора. Хотите подать заявку?", builder.as_markup()