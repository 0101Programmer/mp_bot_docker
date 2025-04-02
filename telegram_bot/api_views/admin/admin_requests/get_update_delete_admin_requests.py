from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from ....models import AdminRequest
from ....serializers import AdminRequestSerializer
from ....tools.check_admin_status import is_user_admin


class AdminRequestListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        requests = AdminRequest.objects.all()
        serializer = AdminRequestSerializer(requests, many=True)
        return Response(serializer.data, status=200)

class UpdateAdminRequestStatusView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, request_id):
        user_id = request.data.get('user_id')
        if not user_id:
            raise ValidationError("user_id is required in the request body.")

        if not is_user_admin(user_id):
            raise PermissionDenied("Только администраторы могут изменять статус заявок.")

        try:
            admin_request = AdminRequest.objects.get(id=request_id)
        except AdminRequest.DoesNotExist:
            raise NotFound("Заявка с указанным ID не найдена.")

        new_status = request.data.get('status')
        comment = request.data.get('comment')

        if new_status == 'rejected' and not comment:
            raise ValidationError("Комментарий обязателен при отклонении заявки.")

        admin_request.status = new_status
        admin_request.comment = comment
        admin_request.save()

        serializer = AdminRequestSerializer(admin_request)
        return Response(serializer.data, status=200)

class DeleteAdminRequestView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, request_id):
        user_id = request.data.get('user_id')
        if not user_id:
            raise ValidationError("user_id is required in the request body.")

        if not is_user_admin(user_id):
            raise PermissionDenied("Только администраторы могут удалять заявки.")

        try:
            admin_request = AdminRequest.objects.get(id=request_id)
        except AdminRequest.DoesNotExist:
            raise NotFound("Заявка с указанным ID не найдена.")

        admin_request.delete()
        return Response({"message": "Заявка успешно удалена."}, status=200)