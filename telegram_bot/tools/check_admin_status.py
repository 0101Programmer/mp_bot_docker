from asgiref.sync import sync_to_async
from ..models import User

async def is_user_admin(user_id: int) -> bool:
    """
    Проверяет, является ли пользователь с указанным ID администратором.
    Использует sync_to_async для выполнения синхронного кода Django ORM в асинхронном контексте.
    :param user_id: Первичный ключ (ID) пользователя
    :return: True, если пользователь администратор, иначе False
    """
    # Оборачиваем синхронный код в sync_to_async
    user = await sync_to_async(User.objects.filter(id=user_id).first)()
    return user.is_admin if user else False