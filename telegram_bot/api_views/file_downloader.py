from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from django.http import FileResponse, HttpResponseNotFound
import os
from django.conf import settings

from ..models import Appeal


class DownloadFileView(APIView):
    # permission_classes = [AllowAny]  # Разрешаем доступ без аутентификации

    def get(self, request, appeal_id):
        try:
            # Находим обращение по ID
            appeal = Appeal.objects.get(id=appeal_id)

            # Проверяем, существует ли файл
            if appeal.file_path and appeal.file_path.storage.exists(appeal.file_path.name):
                # Возвращаем файл как ответ
                return FileResponse(appeal.file_path.open('rb'), as_attachment=True)
            else:
                # Если файл не найден, возвращаем ошибку 404
                return HttpResponseNotFound("Файл не найден.")
        except Appeal.DoesNotExist:
            return HttpResponseNotFound("Обращение не найдено.")