import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from ...models import AdminRequest

logger = logging.getLogger(__name__)

class CheckPendingRequest(APIView):
    """
    Проверяет, есть ли у пользователя активная заявка на получение админ-прав.
    """

    def get(self, request, user_id, *args, **kwargs):
        try:
            # Проверяем наличие активной заявки
            has_pending_request = AdminRequest.objects.filter(user_id=user_id, status='pending').exists()
            return Response({'has_pending_request': has_pending_request})
        except Exception as e:
            logger.error(f"Ошибка при проверке активной заявки: {e}")
            return Response({'detail': 'Произошла ошибка.'}, status=500)