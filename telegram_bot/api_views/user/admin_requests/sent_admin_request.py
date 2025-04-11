from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ....models import User, AdminRequest, StatusChoices
from ....serializers import AdminRequestCreateSerializer
from ....tools.main_logger import logger


class SentAdminRequest(APIView):
    """
    Обрабатывает запросы на получение админ-прав.
    """

    def post(self, request, *args, **kwargs):
        # Валидируем входящие данные
        serializer = AdminRequestCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Получаем данные из запроса
        user_id = serializer.validated_data['user_id']
        admin_position = serializer.validated_data['admin_position']

        try:
            # Находим пользователя
            user = User.objects.get(id=user_id)

            # Проверяем, нет ли активной заявки в статусе 'pending'
            if AdminRequest.objects.filter(user=user, status=StatusChoices.PENDING).exists():
                return Response(
                    {"detail": "У вас уже есть активная заявка на рассмотрении."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Удаляем все отклонённые заявки (status='rejected') для данного пользователя
            deleted_count, _ = AdminRequest.objects.filter(
                user=user, status=StatusChoices.REJECTED
            ).delete()
            if deleted_count > 0:
                logger.info(f"Удалено {deleted_count} отклонённых заявок для пользователя с user_id={user_id}")

            # Создаем новую заявку
            AdminRequest.objects.create(
                user=user,
                admin_position=admin_position,
                status=StatusChoices.PENDING
            )

            return Response(
                {"detail": "Заявка успешно отправлена. Ожидайте одобрения."},
                status=status.HTTP_201_CREATED
            )

        except User.DoesNotExist:
            logger.error(f"Пользователь с user_id={user_id} не найден.")
            return Response(
                {"detail": "Пользователь с указанным user_id не найден."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Логируем ошибку
            logger.error(f"Ошибка при обработке запроса на получение админ-прав: {e}")
            return Response(
                {"detail": "Произошла ошибка. Пожалуйста, попробуйте позже."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )