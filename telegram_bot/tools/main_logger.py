import logging
from django.conf import settings

# Получаем логгер из settings
logger = logging.getLogger(getattr(settings, 'LOGGER_NAME', 'django'))