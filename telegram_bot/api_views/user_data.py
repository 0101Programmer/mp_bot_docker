from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from rest_framework.views import APIView
from django.http import HttpResponseRedirect
from http.cookies import SimpleCookie
from rest_framework.response import Response

from redis_config import redis_client
from ..models import User
from ..serializers import UserSerializer
import base64
import json

import logging

logger = logging.getLogger(__name__)

from django.http import HttpResponseRedirect

class AccountView(APIView):
    def get(self, request, token):
        """
        Проверяет токен и возвращает данные пользователя через API.
        """
        # Проверяем токен в Redis
        telegram_id = redis_client.get(f"token:{token}")
        if not telegram_id:
            return Response({"error": "Доступ запрещён. Токен недействителен."}, status=403)

        # Получаем данные пользователя из базы данных
        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден."}, status=404)

        # Сериализуем данные
        serializer = UserSerializer(user)
        user_data = serializer.data

        # Возвращаем данные в теле ответа
        return Response(user_data, status=200)