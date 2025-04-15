from django.core.management.base import BaseCommand
from django_redis import get_redis_connection

class Command(BaseCommand):
    help = 'Проверяет доступность Redis'

    def handle(self, *args, **options):
        try:
            # Попытка подключиться к Redis
            redis = get_redis_connection("default")
            redis.ping()  # Отправляем PING-запрос
            self.stdout.write(self.style.SUCCESS("Redis is available."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Redis is not available: {e}"))
            exit(1)  # Прерываем выполнение