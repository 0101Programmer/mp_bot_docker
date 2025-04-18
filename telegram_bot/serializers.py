import re
from django.db.utils import IntegrityError

from rest_framework import serializers
from .models import User, Appeal, CommissionInfo, AdminRequest
from decouple import config

# Загрузка конфигурации из .env
MIN_TXT_LENGTH = int(config('MIN_TXT_LENGTH'))  # Минимальная длина текста
MAX_TXT_LENGTH = int(config('MAX_TXT_LENGTH'))  # Максимальная длина текста
MAX_FILE_SIZE = int(config('MAX_FILE_SIZE'))  # Максимальный размер файла в байтах

class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.
    """
    class Meta:
        model = User
        fields = ['id', 'telegram_id', 'username', 'first_name', 'last_name', 'is_admin', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']  # Поля только для чтения

    def validate_telegram_id(self, value):
        """
        Проверка уникальности Telegram ID.
        """
        if User.objects.filter(telegram_id=value).exists():
            raise serializers.ValidationError("Пользователь с таким Telegram ID уже существует.")
        return value


class AppealSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Appeal (для пользователей).
    """
    commission_name = serializers.SerializerMethodField()

    class Meta:
        model = Appeal
        fields = [
            'id',
            'user',
            'commission',
            'commission_name',
            'appeal_text',
            'contact_info',
            'file_path',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_commission_name(self, obj):
        """
        Получение названия комиссии (если она указана).
        """
        return obj.commission.name if obj.commission else "Неизвестная комиссия"

    def validate_appeal_text(self, value):
        """
        Валидация текста обращения.
        """
        if len(value) < MIN_TXT_LENGTH:
            raise serializers.ValidationError(
                f"Текст обращения должен содержать минимум {MIN_TXT_LENGTH} символов."
            )
        if len(value) > MAX_TXT_LENGTH:
            raise serializers.ValidationError(
                f"Текст обращения не должен превышать {MAX_TXT_LENGTH} символов."
            )
        return value

    def validate_contact_info(self, value):
        """
        Валидация контактной информации.
        """
        if value:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            phone_pattern = r'^\+7\d{10}$'
            if not re.match(email_pattern, value) and not re.match(phone_pattern, value):
                raise serializers.ValidationError(
                    "Контактная информация должна быть либо в формате email: example@mail.ru, "
                    "либо в формате номера телефона РФ (+74951234567)."
                )
        return value

    def validate_commission(self, value):
        """
        Валидация комиссии.
        """
        if not value:
            raise serializers.ValidationError("Комиссия не указана.")
        return value

    def validate_file_path(self, value):
        """
        Валидация размера файла.
        """
        if value and value.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                f"Размер файла не должен превышать {MAX_FILE_SIZE / (1024 * 1024)} MB."
            )
        return value

class AppealSerializerForAdmin(serializers.ModelSerializer):
    """
    Сериализатор для модели Appeal (для администраторов).
    """
    commission_name = serializers.SerializerMethodField()

    class Meta:
        model = Appeal
        fields = '__all__'

    def get_commission_name(self, obj):
        """
        Получение названия комиссии (если она указана).
        """
        if obj.commission:
            return obj.commission.name
        return "Комиссия не найдена"

class CommissionInfoSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели CommissionInfo.
    """
    class Meta:
        model = CommissionInfo
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CommissionInfoWriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания/обновления комиссий.
    Проверяет уникальность имени без учета регистра.
    """
    name = serializers.CharField(required=True, allow_blank=False, error_messages={
        'blank': 'Название не может быть пустым',
        'required': 'Название обязательно для заполнения'
    })
    description = serializers.CharField(required=True, allow_blank=False, error_messages={
        'blank': 'Описание не может быть пустым',
        'required': 'Описание обязательно для заполнения'
    })

    class Meta:
        model = CommissionInfo
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']

    def validate_name(self, value):
        """
        Проверяет, что имя комиссии уникально (без учета регистра).
        """
        if not value:
            raise serializers.ValidationError("Название не может быть пустым")

        name_lower = value.lower()
        queryset = CommissionInfo.objects.filter(name__iexact=name_lower)

        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            existing_name = queryset.first().name
            raise serializers.ValidationError(
                f"Название '{value}' уже используется (регистр не учитывается). "
                f"Существующее название: '{existing_name}'"
            )
        return value

    def validate(self, data):
        """
        Общая валидация для всех полей.
        """
        errors = {}

        # Проверка названия
        if 'name' in data and not data['name'].strip():
            errors['name'] = ['Название не может состоять только из пробелов']

        # Проверка описания
        if 'description' in data and not data['description'].strip():
            errors['description'] = ['Описание не может состоять только из пробелов']

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            raise serializers.ValidationError({
                'name': ['Комиссия с таким названием уже существует']
            })

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except IntegrityError as e:
            raise serializers.ValidationError({
                'name': ['Комиссия с таким названием уже существует']
            })


class AdminRequestSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели AdminRequest (для чтения).
    """
    user = serializers.SerializerMethodField()

    class Meta:
        model = AdminRequest
        fields = [
            'id',
            'user',
            'admin_position',
            'status',
            'comment',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_user(self, obj):
        """
        Получение данных пользователя.
        """
        return {
            'id': obj.user.id,
            'username': obj.user.username or None,
            'telegram_id': obj.user.telegram_id
        }


class AdminRequestCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания заявки на получение админ-прав.
    """
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = AdminRequest
        fields = ['id', 'user_id', 'admin_position', 'status', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

    def validate_user_id(self, value):
        """
        Валидация существования пользователя.
        """
        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с указанным ID не найден.")
        if user.is_admin:
            raise serializers.ValidationError("Пользователь уже является администратором.")
        return value