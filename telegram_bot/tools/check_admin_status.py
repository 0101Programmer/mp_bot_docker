from ..models import User

def is_user_admin(user_id: int) -> bool:
    """
    Проверяет, является ли пользователь с указанным ID администратором.
    :param user_id: ID пользователя
    :return: True, если пользователь администратор, иначе False
    """
    try:
        # Ищем пользователя по полю id (первичный ключ)
        user = User.objects.get(id=user_id)
        return user.is_admin
    except User.DoesNotExist:
        # Если пользователь не найден, считаем его не администратором
        return False