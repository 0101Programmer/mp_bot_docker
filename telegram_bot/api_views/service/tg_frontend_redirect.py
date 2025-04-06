from django.http import HttpResponseRedirect, HttpResponseForbidden
from decouple import config

FRONTEND_CORS_ORIGIN = config('FRONTEND_CORS_ORIGIN')


def redirect_to_frontend(request, token):
    """
    Простой переходник для редиректа на фронтенд.
    """
    # Если токен отсутствует, возвращаем статус 403 Forbidden
    if not token:
        return HttpResponseForbidden("Доступ запрещён. Токен отсутствует.")

    # Формируем URL для редиректа на стартовую страницу фронтенда
    frontend_url = f"{FRONTEND_CORS_ORIGIN}/?token={token}"

    # Выполняем редирект
    return HttpResponseRedirect(frontend_url)