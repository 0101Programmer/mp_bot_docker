from rest_framework import serializers
from .models import User, Appeal


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'telegram_id', 'username', 'first_name', 'last_name', 'is_admin']

class AppealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appeal
        fields = '__all__'
