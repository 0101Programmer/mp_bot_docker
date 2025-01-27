from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import User, Notification
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=User)
def track_user_admin_status(sender, instance, **kwargs):
    """
    Сохраняет предыдущее значение is_admin перед сохранением.
    """
    if instance.pk:
        try:
            previous = sender.objects.get(pk=instance.pk)
            instance._is_admin_previous = previous.is_admin
        except sender.DoesNotExist:
            instance._is_admin_previous = False
    else:
        instance._is_admin_previous = False

@receiver(post_save, sender=User)
def notify_admin_status_change(sender, instance, created, **kwargs):
    """
    Создаёт уведомление при изменении статуса администратора.
    """
    if not created:
        if hasattr(instance, '_is_admin_previous'):
            if instance.is_admin != instance._is_admin_previous:
                if instance.is_admin:
                    message = 'Ваш статус администратора был одобрен.'
                else:
                    message = 'Ваш статус администратора был отклонен.'
                
                # Создание объекта Notification
                Notification.objects.create(
                    user=instance,
                    appeal=None,
                    status=message,
                    sent=False
                )
                logger.info(f"Создано уведомление для пользователя {instance.user_id}: {message}")