import secrets
import time
from redis_config import redis_client
import logging

logger = logging.getLogger(__name__)

def generate_token(telegram_id):
    """
    Генерирует уникальный токен и сохраняет его в Redis.
    """
    token = secrets.token_hex(32)  # Генерация 64-символьного токена
    # expiration_time = 3600  # Время жизни токена (в секундах, например, 1 час)
    expiration_time = 300

    # Сохраняем токен в Redis с привязкой к telegram_id
    redis_client.setex(
        f"token:{token}",  # Ключ в Redis
        expiration_time,   # Время жизни токена
        telegram_id        # Значение (telegram_id пользователя)
    )

    logger.info(f"Сгенерирован токен для telegram_id={telegram_id}: {token}")
    return token