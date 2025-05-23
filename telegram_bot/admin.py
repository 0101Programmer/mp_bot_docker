from django.contrib import admin, messages
from .models import User, CommissionInfo, Appeal, Notification, AdminRequest
from .tools.main_logger import logger


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username', 'first_name', 'last_name', 'is_admin', 'created_at')
    search_fields = ('username', 'telegram_id', 'first_name', 'last_name')
    list_filter = ('is_admin', 'created_at')

@admin.register(CommissionInfo)
class CommissionInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)

@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'commission', 'status', 'created_at')
    search_fields = ('user__username', 'appeal_text')
    list_filter = ('status', 'created_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'appeal', 'message_preview', 'sent', 'created_at')
    search_fields = ('user__username', 'message')
    list_filter = ('sent', 'created_at')

    def message_preview(self, obj):
        """
        Отображает первые 50 символов сообщения.
        """
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message

    message_preview.short_description = 'Сообщение'

@admin.register(AdminRequest)
class AdminRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'admin_position', 'status', 'created_at')
    search_fields = ('user__username', 'admin_position')
    list_filter = ('status', 'created_at')
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        """
        Массовое действие: Одобрить выбранные заявки.
        """
        pending_requests = queryset.filter(status__iexact='pending')
        count = pending_requests.count()

        for admin_request in pending_requests:
            try:
                # Обновляем статус заявки
                admin_request.status = 'approved'
                admin_request.save()

                # Обновляем статус пользователя
                user = admin_request.user
                user.is_admin = True
                user.save()
            except Exception as e:
                logger.error(f"Ошибка при обработке заявки {admin_request.id}: {e}")

        self.message_user(
            request,
            f"{count} заявок успешно одобрено.",
            messages.SUCCESS
        )

    approve_requests.short_description = "Одобрить выбранные заявки"

    def reject_requests(self, request, queryset):
        """
        Массовое действие: Отклонить выбранные заявки.
        """
        pending_requests = queryset.filter(status__iexact='pending')
        count = pending_requests.count()

        for admin_request in pending_requests:
            try:
                # Обновляем статус заявки и добавляем комментарий
                admin_request.status = 'rejected'
                admin_request.comment = "Администратор не одобрил заявку."
                admin_request.save()
            except Exception as e:
                logger.error(f"Ошибка при обработке заявки {admin_request.id}: {e}")

        self.message_user(
            request,
            f"{count} заявок успешно отклонено.",
            messages.SUCCESS
        )

    reject_requests.short_description = "Отклонить выбранные заявки"
