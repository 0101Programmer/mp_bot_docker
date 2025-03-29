from rest_framework.views import APIView
import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from redis_config import redis_client
from ..models import User
from ..serializers import UserSerializer

logger = logging.getLogger(__name__)


class UserDataView(APIView):
    def get(self, request, token):
        """
        Проверяет токен и возвращает данные пользователя через API.
        """
        # Проверяем токен в Redis
        telegram_id = redis_client.get(f"token:{token}")
        if not telegram_id:
            return Response(
                {"error": "Доступ запрещён.", "message": "Токен недействителен или истёк срок его действия."},
                status=403
            )

        # Получаем данные пользователя из базы данных
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден.", "message": "Пользователь с указанным Telegram ID не существует."},
                status=404
            )

        # Сериализуем данные
        serializer = UserSerializer(user)
        user_data = serializer.data

        # Возвращаем данные в теле ответа
        return Response(user_data, status=200)