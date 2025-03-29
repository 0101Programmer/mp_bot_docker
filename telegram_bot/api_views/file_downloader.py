from rest_framework.views import APIView

from django.http import FileResponse, HttpResponseNotFound
import os
from django.conf import settings

class DownloadFileView(APIView):
    def get(self, request, file_name):
        # Полный путь к файлу
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        # Проверяем, существует ли файл
        if os.path.exists(file_path):
            # Возвращаем файл как ответ
            return FileResponse(open(file_path, 'rb'), as_attachment=True)
        else:
            # Если файл не найден, возвращаем ошибку 404
            return HttpResponseNotFound("Файл не найден.")