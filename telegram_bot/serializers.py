from rest_framework import serializers
from .models import User, Appeal, CommissionInfo, AdminRequest


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
        if len(value) < 100:
            raise serializers.ValidationError("Текст обращения должен содержать минимум 100 символов.")
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


class AppealSerializerForAdmin(serializers.ModelSerializer):
    """
    Сериализатор для модели Appeal (для администраторов).
    """
    class Meta:
        model = Appeal
        fields = '__all__'


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
    """
    name = serializers.CharField(required=True, allow_blank=False)
    description = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = CommissionInfo
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']


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