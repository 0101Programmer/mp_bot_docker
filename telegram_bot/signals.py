from django.db.models.signals import pre_save, pre_delete
from django.db.utils import IntegrityError
from django.dispatch import receiver

from .models import Notification, Appeal, AdminRequest
from .tools.main_logger import logger


# ======================================================
# Блок обработки сигналов для AdminRequest
# ======================================================

@receiver(pre_save, sender=AdminRequest)
def track_admin_request_status_change(sender, instance, **kwargs):
    """
    Отслеживает изменение статуса заявки и создает уведомление.
    Включает подробную информацию: ID, должность, дату подачи, комментарий.
    """
    if not instance.pk:  # Пропускаем создание новых объектов
        return

    try:
        previous_instance = sender.objects.get(pk=instance.pk)
        previous_status = previous_instance.status
        current_status = instance.status

        if previous_status == current_status:
            return

        logger.info(
            f"Статус заявки {instance.pk} изменен с '{previous_instance.get_status_display()}' "
            f"на '{instance.get_status_display()}'."
        )

        # Форматируем дату создания в удобочитаемый формат
        created_date = instance.created_at.strftime("%d.%m.%Y %H:%M")

        message = ""
        if instance.status == 'approved':
            message = (
                f"🎉 Ваша заявка #{instance.pk} на должность '{instance.admin_position}' одобрена!\n\n"
                f"• Дата подачи: {created_date}\n"
                f"• Должность: {instance.admin_position}\n\n"
                f"Теперь вы имеете доступ к панели администратора. Поздравляем!"
            )
        elif instance.status == 'rejected':
            rejection_reason = instance.comment or "причина не указана"
            message = (
                f"⚠️ Ваша заявка #{instance.pk} на должность '{instance.admin_position}' отклонена.\n\n"
                f"• Дата подачи: {created_date}\n"
                f"• Должность: {instance.admin_position}\n"
                f"• Причина отклонения: {rejection_reason}\n\n"
                f"Вы можете подать новую заявку, исправив указанные замечания."
            )

        if message:
            try:
                Notification.objects.create(
                    user=instance.user,
                    admin_request=instance,
                    message=message,
                    sent=False
                )
                logger.info(f"Уведомление создано для пользователя {instance.user.id}.")
            except IntegrityError as e:
                logger.error(f"Ошибка при создании уведомления: {e}")

    except sender.DoesNotExist:
        logger.warning(f"AdminRequest {instance.pk} не найден при обработке сигнала pre_save")


@receiver(pre_delete, sender=AdminRequest)
def update_user_status_on_delete(sender, instance, **kwargs):
    """
    Сигнал для изменения статуса пользователя перед удалением запроса.
    Создает уведомление о снятии статуса администратора с подробной информацией.
    """
    if instance.user.is_admin:
        created_date = instance.created_at.strftime("%d.%m.%Y %H:%M")
        message = (
            f"🔴 Ваш статус администратора (должность: '{instance.admin_position}') был отозван.\n\n"
            f"• Номер заявки: #{instance.pk}\n"
            f"• Дата подачи: {created_date}\n\n"
            f"Вы можете подать новую заявку на получение прав администратора."
        )

        try:
            Notification.objects.create(
                user=instance.user,
                admin_request=instance,
                message=message,
                sent=False
            )
            logger.info(f"Уведомление о снятии статуса админа создано для пользователя {instance.user.id}.")
        except IntegrityError as e:
            logger.error(f"Ошибка при создании уведомления: {e}")

        instance.user.is_admin = False
        instance.user.save(update_fields=['is_admin'])
        logger.info(f"Статус администратора снят у пользователя {instance.user.id}.")


# ======================================================
# Блок обработки сигналов для Appeal
# ======================================================

@receiver(pre_save, sender=Appeal)
def track_appeal_status_change(sender, instance, **kwargs):
    """
    Отслеживает изменение статуса обращения и создает уведомление.
    Добавляет ID обращения в текст уведомления.
    """
    if not instance.pk:  # Пропускаем создание новых объектов
        return

    try:
        previous_instance = sender.objects.get(pk=instance.pk)
        previous_status = previous_instance.status
        current_status = instance.status

        if previous_status == current_status:
            return

        logger.info(
            f"Статус обращения {instance.pk} изменен с '{previous_instance.get_status_display()}' "
            f"на '{instance.get_status_display()}'."
        )

        commission_name = instance.commission.name if instance.commission else "Неизвестная комиссия"
        message = (
            f"Статус вашего обращения #{instance.pk} в комиссию '{commission_name}' "
            f"изменен на: {instance.get_status_display()}."
        )

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
        logger.warning(f"Appeal {instance.pk} не найден при обработке сигнала pre_save")