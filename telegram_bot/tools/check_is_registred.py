from asgiref.sync import sync_to_async

from ..models import User


async def get_user_by_telegram_id(telegram_id: int) -> User | None:
    """
    Проверяет, зарегистрирован ли пользователь в базе данных.
    Возвращает объект пользователя или None, если пользователь не найден.
    """
    user = await sync_to_async(User.objects.filter(telegram_id=telegram_id).first)()
    return user