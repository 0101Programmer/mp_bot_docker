from django.db.models.signals import pre_save
from django.db.utils import IntegrityError
from django.dispatch import receiver

from .models import Notification, Appeal, AdminRequest
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
                logger.info(
                    f"Статус заявки {instance.pk} изменен с '{previous_instance.get_status_display()}' "
                    f"на '{instance.get_status_display()}'."
                )

                # Формируем текст уведомления
                message = ""
                if instance.status == 'approved':
                    message = "Ваша заявка на административные права была одобрена."
                elif instance.status == 'rejected':
                    message = "Ваша заявка на административные права была отклонена."

                # Создаем уведомление
                try:
                    Notification.objects.create(
                        user=instance.user,
                        appeal=None,
                        message=message,  # Используем поле message вместо status
                        sent=False
                    )
                    logger.info(f"Уведомление создано для пользователя {instance.user.id}.")
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
                logger.info(
                    f"Статус обращения {instance.pk} изменен с '{previous_instance.get_status_display()}' "
                    f"на '{instance.get_status_display()}'."
                )

                # Получаем название комиссии (если она есть)
                commission_name = instance.commission.name if instance.commission else "Неизвестная комиссия"

                # Формируем текст уведомления
                message = (
                    f"Статус вашего обращения в комиссию '{commission_name}' "
                    f"изменен на: {instance.get_status_display()}."
                )

                # Создаем уведомление с информацией о комиссии
                try:
                    Notification.objects.create(
                        user=instance.user,
                        appeal=instance,
                        message=message,
                        sent=False
                    )
                    logger.info(f"Уведомление создано для пользователя {instance.user.id}.")
                except IntegrityError as e:
                    logger.error(f"Ошибка при создании уведомления: {e}")
        except sender.DoesNotExist:
            # Если объект не существует (например, при создании), ничего не делаем
            pass