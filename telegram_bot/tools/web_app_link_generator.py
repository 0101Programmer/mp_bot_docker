from decouple import config
from telegram_bot.tools.secret_token_generator import generate_token
from .main_logger import logger

TELEGRAM_BOT_BACKEND_BASE_URL = config('TELEGRAM_BOT_BACKEND_BASE_URL')

def generate_personal_link(telegram_id: int) -> str:
    """
    Генерирует персональную ссылку на личный кабинет.
    """
    token = generate_token(telegram_id)
    personal_link = f"{TELEGRAM_BOT_BACKEND_BASE_URL}/api/v1/service/frontend_redirect_url/{token}"
    logger.info(f"Generated personal link: {personal_link}")
    return personal_link