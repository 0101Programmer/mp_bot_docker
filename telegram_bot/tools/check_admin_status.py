from ..models import User

def is_user_admin(user_id: int) -> bool:
    """
    Проверяет, является ли пользователь с указанным user_id администратором.
    :param user_id: ID пользователя
    :return: True, если пользователь администратор, иначе False
    """
    try:
        user = User.objects.get(user_id=user_id)
        return user.is_admin
    except User.DoesNotExist:
        # Если пользователь не найден, считаем его не администратором
        return False