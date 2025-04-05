from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import User, Notification, Appeal, AdminRequest
from django.db.utils import IntegrityError

from .tools.main_logger import logger


@receiver(pre_save, sender=AdminRequest)
def track_admin_request_status_change(sender, instance, **kwargs):
    """
    Отслеживает изменение статуса заявки и создает уведомление.
    """
    if instance.pk:  # Проверяем, что объект уже существует в базе данных
        try:
            # Получаем предыдущее состояние объекта из базы данных
            previous_instance = sender.objects.get(pk=instance.pk)
            previous_status = previous_instance.status
            current_status = instance.status

            # Если статус изменился
            if previous_status != current_status:
                logger.info(f"Статус заявки {instance.pk} изменен с '{previous_status}' на '{current_status}'.")

                # Создаем уведомление с информацией о новом статусе
                try:
                    if current_status == 'approved':
                        message = "Ваша заявка на административные права была одобрена."
                    elif current_status == 'rejected':
                        message = "Ваша заявка на административные права была отклонена."

                    Notification.objects.create(
                        user=instance.user,
                        appeal=None,
                        status=message,
                        sent=False
                    )
                    logger.info(f"Уведомление создано для пользователя {instance.user.user_id}.")
                except IntegrityError as e:
                    logger.error(f"Ошибка при создании уведомления: {e}")
        except sender.DoesNotExist:
            # Если объект не существует (например, при создании), ничего не делаем
            pass

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