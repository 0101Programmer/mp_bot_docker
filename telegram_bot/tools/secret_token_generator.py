import secrets
from django.core.cache import cache
from .main_logger import logger

def generate_token(telegram_id):
    """
    Генерирует уникальный токен или возвращает существующий, если он ещё действителен.
    Использует Redis через Django Cache Framework (django-redis).
    """
    # Проверяем, есть ли действующий токен для telegram_id
    existing_token = cache.get(f"user_token:{telegram_id}")
    if existing_token:
        logger.info(f"Возвращён существующий токен для telegram_id={telegram_id}: {existing_token}")
        return existing_token

    # Если действующего токена нет, генерируем новый
    token = secrets.token_hex(32)  # Генерация 64-символьного токена
    expiration_time = 3600  # Время жизни токена (в секундах, например, 1 час)

    # Сохраняем токен в Redis с привязкой к telegram_id
    cache.set(
        f"token:{token}",           # Ключ для токена
        telegram_id,                # Значение (telegram_id пользователя)
        timeout=expiration_time     # Время жизни токена
    )

    # Сохраняем обратную связь: telegram_id -> токен
    cache.set(
        f"user_token:{telegram_id}", # Ключ для обратной связи
        token,                       # Значение (токен)
        timeout=expiration_time      # Время жизни токена
    )

    logger.info(f"Сгенерирован новый токен для telegram_id={telegram_id}: {token}")
    return token