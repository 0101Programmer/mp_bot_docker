from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.utils import IntegrityError

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
        try:
            user_id = request.data.get('user_id')
            if not user_id:
                return Response(
                    {
                        "status": "error",
                        "message": "Требуется user_id",
                        "details": {"user_id": ["Это поле обязательно"]}
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        except AttributeError:
            return Response(
                {
                    "status": "error",
                    "message": "Неверный формат запроса"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not async_to_sync(is_user_admin)(user_id):
            return Response(
                {
                    "status": "error",
                    "message": "Только администраторы могут редактировать комиссии"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            commission = CommissionInfo.objects.get(id=commission_id)
        except CommissionInfo.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "Комиссия не найдена"
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CommissionInfoWriteSerializer(commission, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": "Ошибка валидации",
                    "details": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            serializer.save()
            return Response(
                {
                    "status": "success",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except IntegrityError:
            return Response(
                {
                    "status": "error",
                    "message": "Комиссия с таким названием уже существует"
                },
                status=status.HTTP_400_BAD_REQUEST
            )