from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import User, Notification, Appeal
import logging
from django.db.utils import IntegrityError

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
        # Проверяем, изменился ли статус is_admin
        if hasattr(instance, '_is_admin_previous'):
            if instance.is_admin != instance._is_admin_previous:
                if instance.is_admin:
                    message = 'Ваш статус администратора был одобрен.'
                else:
                    message = 'Ваш статус администратора был отклонен.'

                try:
                    # Пытаемся создать объект Notification
                    Notification.objects.create(
                        user=instance,
                        appeal=None,
                        status=message,
                        sent=False
                    )
                    logger.info(f"Создано уведомление для пользователя {instance.user_id}: {message}")
                except IntegrityError as e:
                    # Логируем ошибку и продолжаем выполнение
                    logger.error(f"Ошибка при создании уведомления для пользователя {instance.user_id}: {e}")

@receiver(pre_save, sender=Appeal)
def track_appeal_status_change(sender, instance, **kwargs):
    """
    Отслеживает изменение статуса обращения и создает уведомление.
    """
    if instance.pk:  # Проверяем, что объект уже существует в базе данных
        try:
            # Получаем предыдущее состояние объекта из базы данных
            previous_instance = sender.objects.get(pk=instance.pk)
            previous_status = previous_instance.status
            current_status = instance.status

            # Если статус изменился
            if previous_status != current_status:
                logger.info(f"Статус обращения {instance.pk} изменен с '{previous_status}' на '{current_status}'.")

                # Получаем название комиссии (если она есть)
                commission_name = instance.commission.name if instance.commission else "Неизвестная комиссия"

                # Создаем уведомление с информацией о комиссии
                try:
                    Notification.objects.create(
                        user=instance.user,
                        appeal=instance,
                        status=f"Статус вашего обращения в комиссию '{commission_name}' изменен на: {current_status}",
                        sent=False
                    )
                    logger.info(f"Уведомление создано для пользователя {instance.user.user_id}.")
                except IntegrityError as e:
                    logger.error(f"Ошибка при создании уведомления: {e}")
        except sender.DoesNotExist:
            # Если объект не существует (например, при создании), ничего не делаем
            pass