# Временная инструкция по запуску

1. **Запуск без Docker:**
   - Установите `USE_DOCKER=0` в `.env`.
   - Запустите: `python no_docker_start_project.py`.

2. **Запуск с Docker:**
   - Установите `USE_DOCKER=1` в `.env`.
   - Запустите: `docker-compose up --build`.

Проект будет доступен по адресу: [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

---

### Настройка окружения

Перед запуском проекта необходимо создать файл `.env` в корневой директории и заполнить его следующими переменными (подставив свои значения для секретных данных):

```ini
# -----------------------------------------------------------------------------
# Джанго-ключ; токен бота
# -----------------------------------------------------------------------------
TELEGRAM_API_TOKEN=your_telegram_bot_token
SECRET_KEY=your_django_secret_key

# -----------------------------------------------------------------------------
# База данных
# -----------------------------------------------------------------------------
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
NO_DOCKER_DB_HOST=localhost
DB_HOST=host.docker.internal
DB_PORT=5432

# -----------------------------------------------------------------------------
# Запуск проекта с докер (1) или без него (0)
# -----------------------------------------------------------------------------
USE_DOCKER=1

# -----------------------------------------------------------------------------
# DJANGO_SUPERUSER (опционально)
# -----------------------------------------------------------------------------
DJANGO_SUPERUSER_NAME=admin
DJANGO_SUPERUSER_PASSWORD=admin123

# -----------------------------------------------------------------------------
# Конфигурация для Redis DB
# -----------------------------------------------------------------------------
NO_DOCKER_REDIS_HOST=localhost
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

---

### **Выполнение миграций**

> Обратите внимание, что URL для базы данных в `settings.py` меняется в зависимости от значения переменной `USE_DOCKER`. Поэтому выполнение миграций отличается:

- **Если запуск проекта без Docker (`USE_DOCKER=0`):**
  - Создайте новые миграции (если необходимо):
    ```bash
    python manage.py makemigrations
    ```
  - Примените миграции:
    ```bash
    python manage.py migrate
    ```

- **Если запуск проекта с Docker (`USE_DOCKER=1`):**
  - Создайте новые миграции (если необходимо) внутри контейнера Django:
    ```bash
    docker exec -it django_web python manage.py makemigrations
    ```
  - Примените миграции внутри контейнера Django:
    ```bash
    docker exec -it django_web python manage.py migrate
    ```
  - Здесь `django_web` — это имя контейнера, указанное в `docker-compose.yml`.

---

> Полная документация будет добавлена позже.