from ..models import User, AdminRequest, StatusChoices
from asgiref.sync import sync_to_async
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def check_admin_requests(user: User):
    """
    Проверяет статус заявки пользователя и разрешает/запрещает новую подачу.
    Возвращает (response_message, reply_markup, allow_submit).
    """
    # Получаем существующую заявку (если есть)
    existing_request = await sync_to_async(
        AdminRequest.objects.filter(user=user).first
    )()

    if not existing_request:
        # Если заявок нет - разрешаем подачу
        builder = InlineKeyboardBuilder()
        builder.button(text="Подать заявку", callback_data="submit_admin_request")
        return (
            "У вас нет статуса администратора. Хотите подать заявку?",
            builder.as_markup(),
            True
        )

    # Обрабатываем по статусам
    if existing_request.status == StatusChoices.APPROVED:
        return (
            "Вы уже являетесь администратором.",
            None,
            False
        )
    elif existing_request.status == StatusChoices.PENDING:
        return (
            "Ваша заявка находится на рассмотрении. Пожалуйста, ожидайте решения.",
            None,
            False
        )
    elif existing_request.status == StatusChoices.REJECTED:
        # Для отклонённой заявки разрешаем подать новую
        builder = InlineKeyboardBuilder()
        builder.button(text="Подать заявку повторно", callback_data="submit_admin_request")

        message = (
            f"Ваша предыдущая заявка была отклонена.\n"
            f"Причина: {existing_request.comment or 'не указана'}\n\n"
            f"Вы можете подать заявку повторно, исправив указанные замечания."
        )
        return message, builder.as_markup(), True