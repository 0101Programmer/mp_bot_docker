from rest_framework.response import Response
from rest_framework.views import APIView

from ....models import AdminRequest, User, StatusChoices
from ....tools.main_logger import logger


class CheckPendingRejectedAcceptedRequest(APIView):
    """
    Проверяет, есть ли у пользователя активная или отклонённая заявка на получение админ-прав.
    """

    def get(self, request, user_id, *args, **kwargs):
        try:
            # Получаем пользователя
            user = User.objects.filter(id=user_id).first()
            if not user:
                return Response({'detail': 'Пользователь не найден.'}, status=404)

            # Если пользователь уже администратор, возвращаем соответствующий ответ
            if user.is_admin:
                return Response({
                    'has_pending_request': False,
                    'last_rejected_request': None,
                    'is_admin': True,
                    'message': 'Пользователь уже является администратором.'
                })

            # Проверяем наличие активной (pending) заявки
            has_pending_request = AdminRequest.objects.filter(user_id=user_id, status=StatusChoices.PENDING).exists()

            # Получаем последнюю отклонённую (rejected) заявку
            rejected_request = (
                AdminRequest.objects
                .filter(user_id=user_id, status=StatusChoices.REJECTED)
                .order_by('-created_at')  # Берём самую последнюю
                .first()
            )

            # Формируем ответ
            response_data = {
                'has_pending_request': has_pending_request,
                'last_rejected_request': None,
                'is_admin': user.is_admin,  # Добавляем флаг is_admin
            }

            if rejected_request:
                response_data['last_rejected_request'] = {
                    'admin_position': rejected_request.admin_position,
                    'comment': rejected_request.comment,
                }

            return Response(response_data)

        except Exception as e:
            logger.error(f"Ошибка при проверке заявки: {e}")
            return Response({'detail': 'Произошла ошибка.'}, status=500)