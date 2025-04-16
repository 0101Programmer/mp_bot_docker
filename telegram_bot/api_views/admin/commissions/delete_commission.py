from asgiref.sync import async_to_sync
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound, ParseError
from rest_framework.exceptions import PermissionDenied, NotFound
from ....models import CommissionInfo
from ....tools.check_admin_status import is_user_admin


class DeleteCommissionView(APIView):

    def delete(self, request, commission_id):
        # Получаем user_id из тела запроса
        try:
            user_id = request.data.get('user_id')
            if not user_id:
                raise ParseError("user_id is required in the request body.")
        except AttributeError:
            raise ParseError("Invalid request body.")

        # Проверяем, является ли пользователь администратором
        if not async_to_sync(is_user_admin)(user_id):
            raise PermissionDenied("Только администраторы могут удалять комиссии.")

        # Ищем комиссию по ID
        try:
            commission = CommissionInfo.objects.get(id=commission_id)
        except CommissionInfo.DoesNotExist:
            raise NotFound("Комиссия с указанным ID не найдена.")

        # Удаляем комиссию
        commission.delete()
        return Response({"message": "Комиссия успешно удалена."}, status=200)