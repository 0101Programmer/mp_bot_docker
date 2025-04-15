import asyncio
import subprocess
import sys
from decouple import config


# === ФУНКЦИЯ ДЛЯ ЗАПУСКА КОМАНДЫ ===
def run_command(command):
    """
    Запускает команду в терминале.
    :param command: Команда для выполнения (список аргументов).
    """
    try:
        process = subprocess.Popen(
            command,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        return process
    except Exception as e:
        print(f"Ошибка при выполнении команды: {' '.join(command)} - {e}")
        sys.exit(1)


# === ОСНОВНАЯ ФУНКЦИЯ ===
async def main():
    # Переменные для хранения процессов
    django_server = frontend_server = bot_process = None

    try:
        print("Запуск всех компонентов...")

        # 1. Запускаем Django сервер
        print("Запуск Django сервера...")
        django_server = run_command(["python", "manage.py", "runserver"])
        print("Django сервер запущен.")

        # 2. Проверяем Redis после запуска Django
        print("Проверка доступности Redis...")
        try:
            subprocess.run(["python", "manage.py", "checkredis"], check=True)
        except subprocess.CalledProcessError:
            print("Redis недоступен. Завершение работы.")
            sys.exit(1)

        # 3. Запускаем фронтенд
        print("Запуск фронтенда...")
        frontend_server = run_command(
            ["cmd", "/c", "cd", "mp-bot-docker-frontend", "&&", "npm", "run", "dev"]
        )
        print("Фронтенд запущен.")

        # 4. Запускаем бота
        print("Запуск Telegram бота...")
        bot_process = run_command(["python", "manage.py", "runbot"])
        print("Telegram бот запущен.")

        print("Все компоненты успешно запущены. Нажмите Ctrl+C для завершения работы.")
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\nПроцесс прерван пользователем. Завершение всех компонентов...")
    finally:
        # Корректное завершение всех процессов
        for process, name in [
            (django_server, "Django сервер"),
            (frontend_server, "Фронтенд сервер"),
            (bot_process, "Telegram бот")
        ]:
            if process and process.poll() is None:
                process.terminate()
                print(f"{name} остановлен.")

        # Ждём завершения всех процессов
        for process, name in [
            (django_server, "Django сервер"),
            (frontend_server, "Фронтенд сервер"),
            (bot_process, "Telegram бот")
        ]:
            if process and process.poll() is None:
                try:
                    process.wait(timeout=5)  # Ждём завершения процесса
                except subprocess.TimeoutExpired:
                    process.kill()
                    print(f"{name} принудительно остановлен.")


# === ТОЧКА ВХОДА ===
if __name__ == "__main__":
    # Проверяем значение USE_DOCKER из .env
    USE_DOCKER = config("USE_DOCKER")

    if USE_DOCKER == "1":
        print("Флаг USE_DOCKER установлен в 1. Сейчас настроена конфигурация для запуска проекта с Docker.")
        sys.exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Завершение работы...")