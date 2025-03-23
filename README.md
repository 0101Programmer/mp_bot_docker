# Временная инструкция по запуску

1. **Запуск без Docker:**
   - Установите `USE_DOCKER=0` в `.env`.
   - Запустите: `python no_docker_start_project.py`.

2. **Запуск с Docker:**
   - Установите `USE_DOCKER=1` в `.env`.
   - Запустите: `docker-compose up --build`.

Проект будет доступен по адресу: [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

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