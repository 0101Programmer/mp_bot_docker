from rest_framework.views import APIView
from rest_framework.response import Response
from redis_config import redis_client


class LogoutView(APIView):
    def post(self, request):
        # Получаем telegram_id из query-параметров
        telegram_id = request.query_params.get('telegram_id')
        if not telegram_id:
            return Response({"error": "telegram_id is required"}, status=400)

        # Удаляем токен из Redis
        user_token_key = f"user_token:{telegram_id}"  # Ключ для обратной связи
        token = redis_client.get(user_token_key)

        if token:
            token_key = f"token:{token}"  # Ключ для токена
            redis_client.delete(token_key)
            redis_client.delete(user_token_key)

        return Response({"message": "Вы успешно вышли из системы."})