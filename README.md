# **mp_bot_docker** 
![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![Vue](https://img.shields.io/badge/vue-3.5.13-green.svg)
![Django](https://img.shields.io/badge/django-latest-green.svg)
![Docker](https://img.shields.io/badge/docker-28.0-blue.svg)

Проект чат-бота Молодежного парламента  

## **Описание проекта**  
`mp_bot_docker` — это многофункциональный чат-бот, созданный для работы с обращениями граждан через платформу Telegram. Проект реализован в современном технологическом стеке, обеспечивая удобство взаимодействия как для пользователей, так и для администраторов.

## **Технологический стек**

### Основные компоненты

- **Фронтенд**:
  - Vue 3
  - Vite
  - Pinia
  - TypeScript
  - TailwindCSS
  - *Сборка*: Node.js v22.14, npm v10.9

- **Бэкенд**:
  - Django
  - Django REST Framework (DRF)
  - Python 3.13
  - Aiogram

- **Базы данных**:
  - PostgreSQL 17.4 (64-bit)
  - Redis 7.4

- **Инфраструктура**:
  - Docker 28.0
  - Docker Compose v2.33 
  - Cloudflare Tunnel

---

### **Функционал для пользователей**  
- Отправка обращений в одну из доступных комиссий.  
- Прикрепление файлов к обращениям.  
- Просмотр статуса своих обращений в реальном времени.  
- Получение уведомлений об изменениях статуса обращений.  

---

### **Функционал для администраторов**  
Система предоставляет полный контроль над базой данных через:  
- **Панель администратора Django:** управление пользователями, заявками, комиссиями и уведомлениями.  
- **Чат-бот:** возможность обработки обращений, изменения их статусов и отправки уведомлений.  
- **Веб-интерфейс:** удобное управление всеми сущностями системы через фронтенд-приложение на Vue.  

---

### **Основные сущности в базе данных**  
1. **Пользователи:** регистрация и управление учетными записями.  
2. **Обращения:** хранение текстовых данных, статусов и прикрепленных файлов.  
3. **Комиссии:** список доступных комиссий для отправки обращений.  
4. **Уведомления:** отправка оповещений пользователям.  

---
## **Подготовка к <u>локальному</u> запуску проекта**

### **Настройка окружения**

Перед запуском проекта необходимо создать файл `.env` в корневой директории и заполнить его следующими переменными 
(подставив свои значения для секретных данных):

```ini
# <- | (backend.env) | ->
# -----------------------------------------------------------------------------
# Секретный ключ Джанго сервера
# -----------------------------------------------------------------------------
SECRET_KEY=...

# -----------------------------------------------------------------------------
# DJANGO_SUPERUSER
# -----------------------------------------------------------------------------
DJANGO_SUPERUSER_NAME=...
DJANGO_SUPERUSER_PASSWORD=...

# <- | (cleanup.env) | ->
# -----------------------------------------------------------------------------
# Настройка для функции очистки отправленных уведомлений
# -----------------------------------------------------------------------------
# Удаляются уведомления старше указанного интервала

# Уведомления старше 0 дней
NOTIFICATION_CLEANUP_DAYS=0
# Уведомления старше 0 часов
NOTIFICATION_CLEANUP_HOURS=0
# Уведомления старше X минут
NOTIFICATION_CLEANUP_MINUTES=X

# Задача очистки запускается каждые Y часов
NOTIFICATION_CLEANUP_INTERVAL_HOURS=Y

# <- | (compose.env) | ->
# -----------------------------------------------------------------------------
# Настройка для COMPOSE_BAKE
# -----------------------------------------------------------------------------
DOCKER_BUILDKIT=1

# <- | (config.env) | ->
# -----------------------------------------------------------------------------
# Запуск приложения с докер (1) или без него (0)
# -----------------------------------------------------------------------------
USE_DOCKER=0

# -----------------------------------------------------------------------------
# Настройка DEBUG (True/False)
# -----------------------------------------------------------------------------
DEBUG=True

# -----------------------------------------------------------------------------
# Конфигурация для размера обращений
# -----------------------------------------------------------------------------
# Длинна текста
MIN_TXT_LENGTH=100
MAX_TXT_LENGTH=1000

# Максимальный размер файла в байтах
MAX_FILE_SIZE=5242880

# -----------------------------------------------------------------------------
# Имя приложения
# -----------------------------------------------------------------------------
APP_NAME=telegram_bot

# <- | (db.env) | ->
# -----------------------------------------------------------------------------
# База данных
# -----------------------------------------------------------------------------
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
NO_DOCKER_DB_HOST=localhost
DB_HOST=host.docker.internal
DB_PORT=5432

# <- | (frontend.env) | ->
# -----------------------------------------------------------------------------
# Базовый URL бэкенда для запросов с фронтенда
# -----------------------------------------------------------------------------
VITE_BACKEND_BASE_URL=http://localhost:8000/telegram_bot

# -----------------------------------------------------------------------------
# Переменная для настройки CORS (она же - базовый url фронтенда)
# -----------------------------------------------------------------------------
FRONTEND_CORS_ORIGIN=http://localhost:5173

# -----------------------------------------------------------------------------
# Переменные для страницы CreateAppeal.vue
# -----------------------------------------------------------------------------
VITE_MIN_TXT_LENGTH=100
VITE_MAX_TXT_LENGTH=1000
VITE_MAX_FILE_SIZE=5242880

# <- | (redis.env) | ->
# -----------------------------------------------------------------------------
# Настройка Redis DB
# -----------------------------------------------------------------------------
NO_DOCKER_REDIS_HOST=127.0.0.1
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASS=foobared

# <- | (telegram_bot.env) | ->
# -----------------------------------------------------------------------------
# Токен телеграм-бота
# -----------------------------------------------------------------------------
TELEGRAM_API_TOKEN=...

# -----------------------------------------------------------------------------
# Базовый URL бэкенда для телеграм бота (телеграм запрещает использование localhost в адресе)
# -----------------------------------------------------------------------------
TELEGRAM_BOT_BACKEND_BASE_URL=http://127.0.0.1:8000/telegram_bot

# -----------------------------------------------------------------------------
# HTTPS хост для использования Telegram WebApp
# -----------------------------------------------------------------------------
TELEGRAM_WEBAPP_HOST=passes-lbs-touched-nano.trycloudflare.com
VITE_TELEGRAM_WEBAPP_HOST=passes-lbs-touched-nano.trycloudflare.com
TELEGRAM_WEBAPP_HOST_FOR_CORS=https://passes-lbs-touched-nano.trycloudflare.com
```

Ещё один вариант, в качестве улучшения структуризации - создать пакет `.env_collection` в корне проекта (также перед запуском) и заполнить его `.env` файлами, которые будут содержать
необходимые значения для определённого блока приложения

```ini
.env_collection/
├── __init__.py
├── backend.env
├── frontend.env
├── telegram_bot.env
├── cleanup.env
└── compose.env
└── ...
```

А затем произвести их мердж командой из *корневой* директории: `python scripts/env_merge.py`. 
После чего в *ней* создастся общий `.env` файл

---

### **Создание виртуального окружения и активация (если оно не создано и не активировано)**
- `python -m venv .venv`
- `.venv\Scripts\activate`

### **Установка зависимостей**
- `pip install -r requirements.txt`

---

## **Запуск проекта**  

**Из корневой директории**

1. **Запуск без Docker:**
   - Установить `USE_DOCKER=0` в `.env`.
   - Запустить Redis (через bash, и если не запущен) `~$ sudo systemctl start redis`.
   - Ввести в терминал: `python no_docker_start_project.py`.


2. **Запуск с Docker + COMPOSE_BAKE:**
   - Установить `USE_DOCKER=1` в `.env`.
   - Запустить Docker Desktop.
   - Ввести в терминал: `python docker_start_project.py`.

> Если требуется полная пересборка (down + bake + up), необходимо ввести в терминал `python docker_start_project.py -d`


---

### **Выполнение миграций**

> URL для базы данных в `settings.py` меняется в зависимости от значения переменной `USE_DOCKER`. Поэтому выполнение миграций отличается:

- **Если запуск проекта без Docker (`USE_DOCKER=0`):**
  - Создать новые миграции (если необходимо) можно через команду:
    ```bash
    python manage.py makemigrations
    ```
  - Применение миграции:
    ```bash
    python manage.py migrate
    ```

- **Если запуск проекта с Docker (`USE_DOCKER=1`):**
  - Создать новые миграции (если необходимо) можно только внутри контейнера Django:
    ```bash
    docker exec -it django_web python manage.py makemigrations
    ```
  - Применение миграции внутри контейнера:
    ```bash
    docker exec -it django_web python manage.py migrate
    ```
  - Здесь `django_web` — это имя контейнера, указанное в `docker-compose.yml`.

---

## **Небольшая демонстрация функционала**

### **Чат-бот**  
- Для начала необходимо пройти первичную регистрацию по команде /start, чтобы данные пользователя отобразились в БД

![Снимок экрана 2025-04-02 122256](https://github.com/user-attachments/assets/ee6bb51f-9c5a-46f9-86df-3dcf3ccf0f93)

![Снимок экрана 2025-04-02 122305](https://github.com/user-attachments/assets/66efd102-7199-4baa-83e5-868043f2a435)

![Снимок экрана 2025-04-02 122313](https://github.com/user-attachments/assets/6ef42461-d912-42ca-86cb-8aef2d4c0377)

- Теперь можно приступать к использованию команд. Например, запросим статус администратора для доступа к расширенному функционалу.

![Снимок экрана 2025-04-02 122324](https://github.com/user-attachments/assets/a8cf5b45-31d1-4581-a92d-8d55553e0544)

![Снимок экрана 2025-04-02 122340](https://github.com/user-attachments/assets/a16b6bb4-e125-4223-81e1-401215cfa4e0)

- Через Джанго админ-панель одобрим заявку

![Снимок экрана 2025-04-02 122353](https://github.com/user-attachments/assets/50139398-b368-459c-9087-c8f72763c3b6)

![Снимок экрана 2025-04-02 122403](https://github.com/user-attachments/assets/b79cb27a-b128-45f0-afed-6405416b0039)

- Увидим, что создалось уведомление об изменении статуса заявки

![Снимок экрана 2025-04-02 122423](https://github.com/user-attachments/assets/a08ef543-f762-4455-8f9d-edb216b5bef2)

- Вскоре получаем его от бота

![Снимок экрана 2025-04-02 122432](https://github.com/user-attachments/assets/7ae10f5c-a2f5-4404-89f8-0793502e8ecb)

- А также увидим соответствующие логи

![Снимок экрана 2025-04-02 122450](https://github.com/user-attachments/assets/df03385e-3943-4952-aa22-2117e6e9a283)

- Теперь можно создать комиссию для написания обращения в неё

![Снимок экрана 2025-04-02 122730](https://github.com/user-attachments/assets/662404d8-a88b-44e3-b991-56637d4c8c8c)

- Заполним необходимые поля и комиссия будет создана

![Снимок экрана 2025-04-02 122758](https://github.com/user-attachments/assets/7f8fd514-7b7e-4a53-8cbc-893c31418499)

- Напишем в неё обращение

![Снимок экрана 2025-04-02 122837](https://github.com/user-attachments/assets/cb5f0a44-7972-4f50-9f79-bb9a2e6cfc86)

![Снимок экрана 2025-04-02 122845](https://github.com/user-attachments/assets/47cbf28f-dc64-4fb6-8a5b-5888d0176351)

![Снимок экрана 2025-04-02 122925](https://github.com/user-attachments/assets/01237b73-89df-4608-b178-2cab3b56e9bc)

![Снимок экрана 2025-04-02 122938](https://github.com/user-attachments/assets/012dde49-8e35-49fd-9764-2d76487e9123)

![Снимок экрана 2025-04-02 123012](https://github.com/user-attachments/assets/fad74c8e-5c43-4dd2-97bb-a98d16cb963b)

- Плавно перейдём к веб-приложению

### **Vue веб-приложение**  

- Для того чтобы получить доступ к нему, необходимо выбрать соответствующую команду в меню, по которой создастся токен для авторизации и поступит ссылка на вход

![capture_250402_123044](https://github.com/user-attachments/assets/68b06a16-700d-44a4-af8d-b31aeab1c9cc)

![Снимок экрана 2025-04-02 123217](https://github.com/user-attachments/assets/3488a544-09a2-49a3-8d15-e98eeea9ffc6)


- На главной странице отображаются пользовательские данные

![capture_250402_123239](https://github.com/user-attachments/assets/b58b856d-b6ca-4e42-9942-bebacd51f48a)

- Увидим только что оставленную заявку на другой странице

![Снимок экрана 2025-04-02 123258](https://github.com/user-attachments/assets/6aa57b9d-502a-4250-8752-096ec6d5ea54)

- Перейдём к функционалу администратора и изменим статус заявки

![Снимок экрана 2025-04-02 123251](https://github.com/user-attachments/assets/ca38e940-33e1-4fa8-aeec-bdcdca4f6041)

- На странице обращений сразу отображаются все, но можно отфильтровать нужные по их ID, а также есть ещё несколько ключевых функций

![capture_250402_123342](https://github.com/user-attachments/assets/97192386-20c0-4ac8-ab99-bd7ebd58d704)

- Например, скачаем файл, нажав на соответствующую надпись

![capture_250402_123402](https://github.com/user-attachments/assets/ace7c1e4-2a00-497a-b8e6-b8208614c00c)

- И изменим статус

![capture_250402_123416](https://github.com/user-attachments/assets/9e3b86b4-83fd-41fe-91af-40b465467056)

![Снимок экрана 2025-04-02 123426](https://github.com/user-attachments/assets/df64d7ee-7692-43c6-8de9-9ba4acdc774e)


- Уведомление об изменении статуса уже создалось в таблице, и скоро бот также отправит его

![Снимок экрана 2025-04-02 123443](https://github.com/user-attachments/assets/9fd7d538-ef55-4daa-bcac-9e9528acbe03)

- Уведомление успешно получено, а новый статус заявки можно увидеть, если нажать на кнопку просмотра обращений 

![Снимок экрана 2025-04-02 123500](https://github.com/user-attachments/assets/28f74daf-7c57-403f-b32f-3dc4b2f5672d)

![Снимок экрана 2025-04-02 123519](https://github.com/user-attachments/assets/586b11d4-7b5b-46d8-9391-5dbeb9a8fcfe)

---

## **Важное замечание**

⚠️ На данный момент проект настроен на работу с портами:  
- **Бэкенд**: `8000`  
- **Фронтенд**: `5173` 

При возникновении неожиданных ошибок:  
1. Остановить приложение  
2. Убедиться, что порты не заняты другими процессами 
3. Завершить все процессы на используемых портах из корневой директории:
   ```bash
   python scripts/clear_ports.py
   ```
---

## **Дальнейшие планы**

> Планируется добавление нового функционала:
> - разграничение прав для администраторов;
> - обновление фронтенда под Telegram WebApp
> - улучшение интерфейса.
---