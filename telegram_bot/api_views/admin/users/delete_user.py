from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound, ParseError
from ....models import User
from ....tools.check_admin_status import is_user_admin


class DeleteUserView(APIView):

    def delete(self, request, user_id):
        # Получаем admin_id из тела запроса
        try:
            admin_id = request.data.get('admin_id')
            if not admin_id:
                raise ParseError("admin_id is required in the request body.")
        except AttributeError:
            raise ParseError("Invalid request body.")

        # Проверяем, является ли пользователь администратором
        if not is_user_admin(admin_id):
            raise PermissionDenied("Только администраторы могут удалять пользователей.")

        # Проверяем, что администратор не пытается удалить самого себя
        if int(admin_id) == user_id:
            raise PermissionDenied("Администратор не может удалить самого себя.")

        # Ищем пользователя по ID
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound("Пользователь с указанным ID не найден.")

        # Удаляем пользователя
        user.delete()
        return Response({"message": "Пользователь успешно удален."}, status=200)