import asyncio
from datetime import timedelta

from asgiref.sync import sync_to_async
from decouple import config
from django.utils.timezone import now

from .main_logger import logger
from ..models import Notification


async def delete_old_notifications(days: int = 7, hours: int = 0, minutes: int = 0):
    """
    Удаляет старые отправленные уведомления на основе указанного интервала.
    :param days: Количество дней для интервала (по умолчанию 7).
    :param hours: Количество часов для интервала (по умолчанию 0).
    :param minutes: Количество минут для интервала (по умолчанию 0).
    """
    try:
        # Проверяем, что хотя бы один из параметров больше нуля
        if days <= 0 and hours <= 0 and minutes <= 0:
            raise ValueError("Хотя бы один из параметров (дни, часы, минуты) должен быть больше нуля.")

        # Определяем дату, после которой уведомления считаются "старыми"
        cutoff_date = now() - timedelta(days=days, hours=hours, minutes=minutes)

        # Получаем и удаляем старые отправленные уведомления
        deleted_count = await sync_to_async(Notification.objects.filter(
            sent=True, created_at__lt=cutoff_date
        ).delete)()

        logger.info(f"Удалено {deleted_count[0]} старых отправленных уведомлений.")
    except Exception as e:
        logger.error(f"Ошибка при удалении старых уведомлений: {e}")


async def start_notification_cleanup_task():
    """
    Запускает задачу периодической очистки старых отправленных уведомлений.
    Параметры берутся из конфигурации.
    """
    days = int(config('NOTIFICATION_CLEANUP_DAYS', default=7))
    hours = int(config('NOTIFICATION_CLEANUP_HOURS', default=0))
    minutes = int(config('NOTIFICATION_CLEANUP_MINUTES', default=0))

    interval_hours = int(config('NOTIFICATION_CLEANUP_INTERVAL_HOURS', default=24))
    # Интервал между запусками очистки (в часах, берётся из конфигурации).
    # Пример: interval_hours=24 означает, что задача запускается каждые 24 часа.

    logger.info(f"Задача очистки уведомлений запущена с интервалом {interval_hours} часов.")
    interval_seconds = interval_hours * 3600  # Переводим часы в секунды

    while True:
        try:
            await delete_old_notifications(days=days, hours=hours, minutes=minutes)
        except Exception as e:
            logger.error(f"Ошибка при выполнении очистки уведомлений: {e}")

        await asyncio.sleep(interval_seconds)