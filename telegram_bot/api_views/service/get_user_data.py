from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from ...models import User
from ...serializers import UserSerializer


class UserDataView(APIView):
    def post(self, request):
        """
        Возвращает данные пользователя по Telegram ID, переданному в теле запроса.
        """

        # Извлекаем telegram_id из тела запроса
        telegram_id = request.data.get('telegramId')

        # Проверяем, что telegram_id присутствует
        if not telegram_id:
            return Response(
                {"error": "Неверный запрос.", "message": "Поле 'telegramId' обязательно."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Пытаемся найти пользователя в базе данных
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден.", "message": "Пользователь с указанным Telegram ID не существует."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Сериализуем данные пользователя
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)