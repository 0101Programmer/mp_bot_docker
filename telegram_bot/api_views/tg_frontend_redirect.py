from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import redirect
import redis
from django.conf import settings

def redirect_to_frontend(request, token):
    """
    Простой переходник для редиректа на фронтенд.
    """
    # Если токен отсутствует, возвращаем статус 403 Forbidden
    if not token:
        return HttpResponseForbidden("Доступ запрещён. Токен отсутствует.")

    # Формируем URL для редиректа на фронтенд
    frontend_url = f"http://localhost:5175/account?token={token}"

    # Выполняем редирект
    return HttpResponseRedirect(frontend_url)