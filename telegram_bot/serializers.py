from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'telegram_id', 'username', 'first_name', 'last_name', 'is_admin']