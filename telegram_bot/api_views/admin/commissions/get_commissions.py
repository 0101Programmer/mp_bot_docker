from rest_framework.views import APIView
from rest_framework.response import Response
from ....models import CommissionInfo
from ....serializers import CommissionInfoSerializer

class CommissionListView(APIView):
    def get(self, request):
        commissions = CommissionInfo.objects.all()
        serializer = CommissionInfoSerializer(commissions, many=True)
        return Response(serializer.data)