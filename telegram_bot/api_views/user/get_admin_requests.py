import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from ...models import AdminRequest

logger = logging.getLogger(__name__)

import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from ...models import AdminRequest

logger = logging.getLogger(__name__)

class CheckPendingRejectedRequest(APIView):
    """
    Проверяет, есть ли у пользователя активная или отклонённая заявка на получение админ-прав.
    """

    def get(self, request, user_id, *args, **kwargs):
        try:
            # Проверяем наличие активной заявки
            has_pending_request = AdminRequest.objects.filter(user_id=user_id, status='pending').exists()

            # Проверяем последнюю отклонённую заявку
            rejected_request = (
                AdminRequest.objects
                .filter(user_id=user_id, status='rejected')
                .order_by('-timestamp')  # Берём самую последнюю
                .first()
            )

            response_data = {
                'has_pending_request': has_pending_request,
                'last_rejected_request': None,
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