from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from ....models import Appeal
from ....serializers import AppealSerializerForAdmin
from ....tools.check_admin_status import is_user_admin


class AppealListForAdminView(APIView):

    def get(self, request):
        appeals = Appeal.objects.all()
        serializer = AppealSerializerForAdmin(appeals, many=True)
        return Response(serializer.data, status=200)

class UpdateAppealStatusView(APIView):

    def put(self, request, appeal_id):
        # Получаем user_id из тела запроса
        user_id = request.data.get('user_id')
        if not user_id:
            raise ValidationError("user_id is required in the request body.")

        # Проверяем, является ли пользователь администратором
        if not is_user_admin(user_id):
            raise PermissionDenied("Только администраторы могут изменять статус обращения.")

        try:
            appeal = Appeal.objects.get(id=appeal_id)
        except Appeal.DoesNotExist:
            raise NotFound("Обращение с указанным ID не найдено.")

        new_status = request.data.get('status')
        if not new_status:
            raise ValidationError("status is required in the request body.")

        appeal.status = new_status
        appeal.save()
        return Response({"message": "Статус успешно обновлен."}, status=200)

class DeleteAppealForAdminView(APIView):

    def delete(self, request, appeal_id):
        # Получаем user_id из тела запроса
        user_id = request.data.get('user_id')
        if not user_id:
            raise ValidationError("user_id is required in the request body.")

        # Проверяем, является ли пользователь администратором
        if not is_user_admin(user_id):
            raise PermissionDenied("Только администраторы могут удалять обращения.")

        try:
            appeal = Appeal.objects.get(id=appeal_id)
        except Appeal.DoesNotExist:
            raise NotFound("Обращение с указанным ID не найдено.")

        # Удаляем связанный файл, если он существует
        if appeal.file_path:
            try:
                # Удаляем файл с диска
                appeal.file_path.delete(save=False)
            except Exception as e:
                # Логируем ошибку, но продолжаем выполнение
                print(f"Ошибка при удалении файла: {e}")

        # Удаляем обращение из базы данных
        appeal.delete()

        return Response({"message": "Обращение успешно удалено."}, status=200)