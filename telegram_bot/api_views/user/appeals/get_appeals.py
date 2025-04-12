from rest_framework.views import APIView
from rest_framework.response import Response
from ....models import Appeal
from ....serializers import AppealSerializer

class AppealListView(APIView):

    def get(self, request):
        # Получаем user_id из query-параметров
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required"}, status=400)

        # Получаем все заявки для указанного пользователя с использованием select_related
        appeals = Appeal.objects.filter(user_id=user_id).select_related('commission')
        serializer = AppealSerializer(appeals, many=True)
        return Response(serializer.data)