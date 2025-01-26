# Базовый образ Python
FROM python:3.9-slim-buster

# Переменная окружения
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    default-libmysqlclient-dev

# Создаём рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь проект
COPY . /app

# Указываем переменные окружения (в т.ч. DJANGO_SETTINGS_MODULE, если нужно)
ENV DJANGO_SETTINGS_MODULE=mp_bot.settings

# По умолчанию — запуск бота
CMD ["python", "manage.py", "runbot"]