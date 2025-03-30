import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from ..models import User, CommissionInfo, Appeal
from ..serializers import AppealSerializer

logger = logging.getLogger(__name__)

class CreateAppealView(APIView):
    def post(self, request):
        try:
            # Извлекаем данные из запроса
            user_id = request.data.get('user_id')
            commission_id = request.data.get('commission_id')
            appeal_text = request.data.get('appeal_text')
            contact_info = request.data.get('contact_info')
            file = request.FILES.get('file')  # Получаем загруженный файл

            # Проверяем обязательные поля
            if not user_id:
                return Response(
                    {"errors": {
                        "non_field_errors": ["Поле user_id является обязательным."]}},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Находим пользователя
            try:
                user = User.objects.get(user_id=user_id)
            except ObjectDoesNotExist:
                return Response(
                    {"errors": {"user_id": ["Пользователь с указанным ID не найден."]}},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Находим комиссию (если указана)
            commission = None
            if commission_id:
                try:
                    commission = CommissionInfo.objects.get(id=commission_id)
                except ObjectDoesNotExist:
                    return Response(
                        {"errors": {"commission_id": ["Комиссия с указанным ID не найдена."]}},
                        status=status.HTTP_404_NOT_FOUND
                    )

            # Создаем объект для сериализации
            data = {
                'user': user.user_id,
                'commission': commission.id if commission else None,
                'appeal_text': appeal_text,
                'contact_info': contact_info,
            }

            # Если есть файл, добавляем его в данные
            if file:
                data['file_path'] = file

            # Валидируем данные через сериализатор
            serializer = AppealSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Обращение успешно создано."}, status=status.HTTP_201_CREATED)
            else:
                # Возвращаем ошибки валидации в ожидаемом формате
                return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Ошибка при создании обращения: {e}")
            return Response(
                {"errors": {"non_field_errors": ["Произошла непредвиденная ошибка при создании обращения."]}},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )