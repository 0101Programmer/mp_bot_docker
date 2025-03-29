from django.http import HttpResponseRedirect, HttpResponseForbidden


def redirect_to_frontend(request, token):
    """
    Простой переходник для редиректа на фронтенд.
    """
    # Если токен отсутствует, возвращаем статус 403 Forbidden
    if not token:
        return HttpResponseForbidden("Доступ запрещён. Токен отсутствует.")

    # Формируем URL для редиректа на стартовую страницу фронтенда
    frontend_url = f"http://localhost:5173/?token={token}"

    # Выполняем редирект
    return HttpResponseRedirect(frontend_url)