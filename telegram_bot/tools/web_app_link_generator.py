from decouple import config

TELEGRAM_WEBAPP_HOST = config('TELEGRAM_WEBAPP_HOST')
APP_NAME = config('APP_NAME')
FRONTEND_CORS_ORIGIN = config('FRONTEND_CORS_ORIGIN')

def generate_personal_link() -> str:
    """
    Генерирует ссылку на личный кабинет для Telegram WebApp.
    """
    personal_link = f"https://{TELEGRAM_WEBAPP_HOST}"
    return personal_link