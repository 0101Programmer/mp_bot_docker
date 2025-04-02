import logging

from telegram_bot.tools.secret_token_generator import generate_token

logger = logging.getLogger(__name__)

def generate_personal_link(telegram_id: int) -> str:
    """
    Генерирует персональную ссылку на личный кабинет.
    """
    token = generate_token(telegram_id)
    personal_link = f"http://127.0.0.1:8000/telegram_bot/frontend_redirect_url/{token}"
    logger.info(f"Generated personal link: {personal_link}")
    return personal_link