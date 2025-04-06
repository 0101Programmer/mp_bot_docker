from rest_framework.views import APIView
from rest_framework.response import Response
from ....models import Appeal

from ....tools.main_logger import logger

class DeleteAppealView(APIView):

    def delete(self, request, appeal_id):
        try:
            # Получаем user_id из query-параметров
            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response({"error": "user_id is required"}, status=400)

            # Преобразуем user_id в целое число
            try:
                user_id = int(user_id)
            except ValueError:
                return Response({"error": "user_id must be an integer"}, status=400)

            # Находим обращение по ID и user_id
            try:
                appeal = Appeal.objects.get(id=appeal_id, user_id=user_id)
            except Appeal.DoesNotExist:
                return Response({"error": "Обращение не найдено."}, status=404)

            # Удаляем связанный файл, если он существует
            if appeal.file_path:
                try:
                    # Удаляем файл через метод delete() FileField
                    appeal.file_path.delete(save=False)
                except Exception as e:
                    logger.error(f"Ошибка при удалении файла: {str(e)}")
                    # Можно игнорировать ошибку или вернуть предупреждение
                    return Response({
                        "message": "Обращение удалено, но файл не был удален.",
                        "details": str(e)
                    })

            # Удаляем обращение из базы данных
            appeal.delete()

            return Response({"message": "Обращение успешно удалено."})

        except Exception as e:
            logger.error("Error:", str(e))  # Логируем ошибку
            return Response({"error": f"Ошибка при удалении обращения: {str(e)}"}, status=500)