from asgiref.sync import async_to_sync
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView

from ....models import CommissionInfo
from ....serializers import CommissionInfoSerializer, CommissionInfoWriteSerializer
from ....tools.check_admin_status import is_user_admin


class CommissionDetailView(APIView):

    def get(self, request, commission_id):
        try:
            commission = CommissionInfo.objects.get(id=commission_id)
        except CommissionInfo.DoesNotExist:
            raise NotFound("Комиссия с указанным ID не найдена.")

        serializer = CommissionInfoSerializer(commission)
        return Response(serializer.data)

class UpdateCommissionView(APIView):

    def put(self, request, commission_id):
        # Получаем user_id из тела запроса
        try:
            user_id = request.data.get('user_id')
            if not user_id:
                raise ParseError("user_id is required in the request body.")
        except AttributeError:
            raise ParseError("Invalid request body.")

        # Проверяем, является ли пользователь администратором
        if not async_to_sync(is_user_admin)(user_id):
            raise PermissionDenied("Только администраторы могут редактировать комиссии.")

        # Ищем комиссию по ID
        try:
            commission = CommissionInfo.objects.get(id=commission_id)
        except CommissionInfo.DoesNotExist:
            raise NotFound("Комиссия с указанным ID не найдена.")

        # Обновляем данные комиссии
        serializer = CommissionInfoWriteSerializer(commission, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)