import asyncio
from asgiref.sync import sync_to_async
from aiogram.exceptions import TelegramBadRequest

from ..models import Notification
from .main_logger import logger


async def send_pending_notifications(bot):
    """
    Проверяет наличие непосланных уведомлений и отправляет их пользователям.
    Если чат не найден (chat not found), уведомление удаляется.
    :param bot: Экземпляр бота (aiogram.Bot).
    """
    while True:
        try:
            # Получаем все непосланные уведомления (sent=False)
            pending_notifications = await sync_to_async(list)(
                Notification.objects.filter(sent=False).select_related('user')
            )

            for notification in pending_notifications:
                user = notification.user
                telegram_id = user.telegram_id

                if telegram_id:  # Убедимся, что у пользователя есть Telegram ID
                    try:
                        # Отправляем сообщение пользователю
                        await bot.send_message(telegram_id, notification.message)

                        # Обновляем статус уведомления на "отправлено"
                        notification.sent = True
                        await sync_to_async(notification.save)()
                        logger.info(
                            f"Уведомление отправлено пользователю {user.id} (Telegram ID: {telegram_id})"
                        )

                    except TelegramBadRequest as e:
                        # Проверяем, является ли ошибка "chat not found"
                        if "chat not found" in str(e):
                            logger.error(
                                f"Чат не найден для пользователя {user.id} (Telegram ID: {telegram_id}). Удаляем уведомление."
                            )
                            # Удаляем уведомление
                            await sync_to_async(notification.delete)()
                        else:
                            # Логируем другие ошибки Telegram API
                            logger.error(
                                f"Не удалось отправить уведомление пользователю {user.id}: {e}"
                            )

                    except Exception as e:
                        # Логируем остальные ошибки
                        logger.error(
                            f"Произошла ошибка при отправке уведомления пользователю {user.id}: {e}"
                        )

                else:
                    logger.error(f"У пользователя {user.id} отсутствует Telegram ID.")

            # Ждем некоторое время перед следующей проверкой
            await asyncio.sleep(60)  # Проверяем каждые 60 секунд

        except Exception as e:
            # Логируем ошибку, если произошла проблема в основном цикле
            logger.error(f"Произошла ошибка при обработке уведомлений: {e}")
            await asyncio.sleep(60)  # Продолжаем проверку после ошибки


async def start_notification_task(bot):
    """
    Запускает задачу отправки уведомлений.
    :param bot: Экземпляр бота (aiogram.Bot).
    """
    logger.info("Задача отправки уведомлений запущена.")
    # Возвращаем корутину для выполнения в фоновом режиме
    return asyncio.create_task(send_pending_notifications(bot))