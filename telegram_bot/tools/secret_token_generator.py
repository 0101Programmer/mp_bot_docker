import secrets
import time
from redis_config import redis_client
import logging

logger = logging.getLogger(__name__)

def generate_token(telegram_id):
    """
    Генерирует уникальный токен или возвращает существующий, если он ещё действителен.
    """
    # Проверяем, есть ли действующий токен для telegram_id
    existing_token = redis_client.get(f"user_token:{telegram_id}")
    if existing_token:
        token = existing_token  # Уже строка, не нужно декодировать
        logger.info(f"Возвращён существующий токен для telegram_id={telegram_id}: {token}")
        return token

    # Если действующего токена нет, генерируем новый
    token = secrets.token_hex(32)  # Генерация 64-символьного токена
    expiration_time = 3600  # Время жизни токена (в секундах, например, 1 час)

    # Сохраняем токен в Redis с привязкой к telegram_id
    redis_client.setex(
        f"token:{token}",           # Ключ для токена
        expiration_time,            # Время жизни токена
        telegram_id                 # Значение (telegram_id пользователя)
    )

    # Сохраняем обратную связь: telegram_id -> токен
    redis_client.setex(
        f"user_token:{telegram_id}", # Ключ для обратной связи
        expiration_time,             # Время жизни токена
        token                        # Значение (токен)
    )

    logger.info(f"Сгенерирован новый токен для telegram_id={telegram_id}: {token}")
    return token