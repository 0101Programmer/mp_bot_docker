from asgiref.sync import async_to_sync
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from ....serializers import CommissionInfoWriteSerializer
from ....tools.check_admin_status import is_user_admin


class CreateCommissionView(APIView):

    def post(self, request):
        # Получаем user_id из запроса
        user_id = request.data.get('user_id')

        # Проверяем, является ли пользователь администратором
        if not async_to_sync(is_user_admin)(user_id):
            raise PermissionDenied("Только администраторы могут создавать комиссии.")

        # Используем сериализатор для создания
        serializer = CommissionInfoWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)

        return Response(serializer.errors, status=400)