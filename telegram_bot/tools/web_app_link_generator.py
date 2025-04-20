from decouple import config
from telegram_bot.tools.secret_token_generator import generate_token

TELEGRAM_WEBAPP_HOST = config('TELEGRAM_WEBAPP_HOST')
APP_NAME = config('APP_NAME')
FRONTEND_CORS_ORIGIN = config('FRONTEND_CORS_ORIGIN')


# def generate_personal_link(telegram_id: int) -> str:
#     """
#     Генерирует персональную ссылку на личный кабинет.
#     """
#     token = generate_token(telegram_id)
#     personal_link = f"https://{TELEGRAM_WEBAPP_HOST}/{APP_NAME}/api/v1/service/frontend_redirect_url/{token}"
#     return personal_link

def generate_personal_link() -> str:
    """
    Генерирует ссылку на личный кабинет для Telegram WebApp.
    """
    personal_link = f"https://{TELEGRAM_WEBAPP_HOST}/{FRONTEND_CORS_ORIGIN}"
    return personal_link