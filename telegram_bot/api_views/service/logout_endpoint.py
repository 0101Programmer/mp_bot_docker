from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache


class LogoutView(APIView):
    def post(self, request):
        # Получаем telegram_id из query-параметров
        telegram_id = request.query_params.get('telegram_id')
        if not telegram_id:
            return Response({"error": "telegram_id is required"}, status=400)

        # Удаляем токен из кэша
        user_token_key = f"user_token:{telegram_id}"  # Ключ для обратной связи
        token = cache.get(user_token_key)  # Получаем токен из кэша

        if token:
            token_key = f"token:{token}"  # Ключ для токена
            cache.delete(token_key)  # Удаляем токен из кэша
            cache.delete(user_token_key)  # Удаляем связь между telegram_id и токеном

        return Response({"message": "Вы успешно вышли из системы."})