from django.contrib import admin
from .models import User, CommissionInfo, Appeal, Notification, AdminRequest
from django.contrib import messages

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'telegram_id', 'username', 'first_name', 'last_name', 'is_admin')
    search_fields = ('username', 'user_id', 'telegram_id', 'first_name', 'last_name')
    list_filter = ('is_admin',)

@admin.register(CommissionInfo)
class CommissionInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'id', 'user', 'commission', 'status')
    search_fields = ('user__username', 'id')
    list_filter = ('status',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'appeal', 'status', 'sent')
    search_fields = ('user__username', 'appeal__id')
    list_filter = ('status', 'sent')

@admin.register(AdminRequest)
class AdminRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'admin_position', 'timestamp', 'status')
    search_fields = ('user__username', 'user__telegram_id', 'admin_position')
    list_filter = ('status',)
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        for admin_request in queryset.filter(status='pending'):
            admin_request.status = 'approved'
            admin_request.save()

            # Обновляем статус пользователя
            user = admin_request.user
            user.is_admin = True
            user.save()

        messages.success(request, "Выбранные заявки успешно одобрены.")

    approve_requests.short_description = "Одобрить выбранные заявки"

    def reject_requests(self, request, queryset):
        for admin_request in queryset.filter(status='pending'):
            admin_request.status = 'rejected'
            admin_request.comment = "Администратор не одобрил заявку."  # Пример комментария
            admin_request.save()

        messages.success(request, "Выбранные заявки успешно отклонены.")

    reject_requests.short_description = "Отклонить выбранные заявки"
