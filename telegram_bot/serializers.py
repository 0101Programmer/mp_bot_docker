import re

from rest_framework import serializers
from .models import User, Appeal, CommissionInfo


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'telegram_id', 'username', 'first_name', 'last_name', 'is_admin']

class AppealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appeal
        fields = ['id', 'user', 'commission', 'appeal_text', 'contact_info', 'file_path', 'status']

    def validate_appeal_text(self, value):
        if len(value) < 100:
            raise serializers.ValidationError("Текст обращения должен содержать минимум 100 символов.")
        return value

    def validate_contact_info(self, value):
        if value:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            phone_pattern = r'^\+7\d{10}$'
            if not re.match(email_pattern, value) and not re.match(phone_pattern, value):
                raise serializers.ValidationError("Контактная информация должна быть либо "
                                                  "в формате email: example@mail.ru "
                                                  "либо в формате номера телефона РФ (+74951234567).")
        return value

    def validate_commission(self, value):
        if not value:
            raise serializers.ValidationError("Комиссия не указана.")
        return value

class AppealSerializerForAdmin(serializers.ModelSerializer):
    class Meta:
        model = Appeal
        fields =  '__all__'

class CommissionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionInfo
        fields = ['id', 'name', 'description']


# Сериализатор для создания/обновления комиссий (POST/PUT-запросы)
class CommissionInfoWriteSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=True, allow_blank=False)  # Обязательное поле
    description = serializers.CharField(required=True, allow_blank=False)  # Обязательное поле

    class Meta:
        model = CommissionInfo
        fields = ['id', 'name', 'description']
