from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AdminRequest

@receiver(post_save, sender=AdminRequest)
def handle_admin_request(sender, instance, **kwargs):
    """
    Сигнал для обработки заявки на роль администратора.
    """
    if instance.status == 'approved' and not instance.user.is_admin:
        # Назначаем пользователя администратором
        instance.user.is_admin = True
        instance.user.save()
    elif instance.status == 'rejected' and instance.user.is_admin:
        # Логика на случай отклонения заявки (опционально)
        instance.user.is_admin = False
        instance.user.save()