import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import Appeal

class DeleteAppealView(APIView):

    def delete(self, request, appeal_id):
        try:
            # Получаем user_id из query-параметров
            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response({"error": "user_id is required"}, status=400)

            # Находим обращение по ID и user_id
            appeal = Appeal.objects.get(id=appeal_id, user_id=user_id)

            # Удаляем связанный файл, если он существует
            if appeal.file_path:
                file_path = os.path.join(settings.BASE_DIR, appeal.file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)

            # Удаляем обращение из базы данных
            appeal.delete()

            return Response({"message": "Обращение успешно удалено."})
        except Appeal.DoesNotExist:
            return Response({"error": "Обращение не найдено."}, status=404)