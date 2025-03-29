from django.core.management.base import BaseCommand
from redis_config import redis_client
from ...tools.secret_token_generator import generate_token

class Command(BaseCommand):
    help = 'Генерирует секретные токены'

    def handle(self, *args, **kwargs):
        token = generate_token(telegram_id=123456789)
        self.stdout.write(self.style.SUCCESS(f'Токен сгенерирован: {token}'))