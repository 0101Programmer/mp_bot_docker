from django.contrib import admin
from .models import User, CommissionInfo, Appeal, Notification

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username')

@admin.register(CommissionInfo)
class CommissionInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'commission', 'status')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'appeal', 'status', 'sent')