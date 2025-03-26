from django.db import models
from asgiref.sync import sync_to_async

class User(models.Model):
    user_id = models.BigAutoField(primary_key=True)  # Автоматически генерируется
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username or f"{self.first_name} {self.last_name}" or str(self.user_id)

class CommissionInfo(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Appeal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    commission = models.ForeignKey(CommissionInfo, on_delete=models.SET_NULL, null=True)
    appeal_text = models.TextField()
    contact_info = models.CharField(max_length=255, null=True, blank=True)
    file_path = models.CharField(max_length=1024, null=True, blank=True)
    status = models.CharField(max_length=255, default='Новое')

    def __str__(self):
        return f"Appeal #{self.id} from {self.user}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    appeal = models.ForeignKey(Appeal, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=255)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for appeal {self.appeal_id} - {self.status}"

class AdminRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    admin_position = models.CharField(max_length=255)  # Новое поле для должности администратора
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    comment = models.TextField(blank=True, null=True)  # Комментарий администратора при отклонении

    def __str__(self):
        return f"AdminRequest от {self.user} - {self.get_status_display()}"
