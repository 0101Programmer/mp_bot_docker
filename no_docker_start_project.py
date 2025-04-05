import asyncio
import os
import subprocess
import sys


# === ФУНКЦИЯ ДЛЯ ЗАПУСКА КОМАНДЫ ===
def run_command(command, cwd=None):
    """
    Запускает команду в терминале.
    :param command: Команда для выполнения (список аргументов).
    :param cwd: Директория, из которой запускать команду (опционально).
    """
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        return process
    except Exception as e:
        print(f"Ошибка при выполнении команды: {e}")
        sys.exit(1)

# === ОСНОВНАЯ ФУНКЦИЯ ===
async def main():
    # Переменные для хранения процессов
    django_server = None
    frontend_server = None
    bot_process = None

    try:
        # Запускаем Django сервер
        print("Запуск Django сервера...")
        django_server = run_command(["python", "manage.py", "runserver"])

        # Запускаем фронтенд
        print("Запуск фронтенда...")
        if os.name == "nt":  # Windows
            frontend_server = run_command(
                ["cmd", "/c", "cd", "mp-bot-docker-frontend", "&&", "npm", "run", "dev"]
            )
        else:  # Linux/macOS
            frontend_server = run_command(
                ["bash", "-c", "cd mp-bot-docker-frontend && npm run dev"]
            )

        # Запускаем бота
        print("Запуск Telegram бота...")
        bot_process = run_command(["python", "manage.py", "runbot"])

        # Ждём завершения процессов (бесконечный цикл)
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\nПроцесс прерван пользователем.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        # Корректное завершение всех процессов
        if django_server and django_server.poll() is None:
            django_server.terminate()
            print("Django сервер остановлен.")

        if frontend_server and frontend_server.poll() is None:
            frontend_server.terminate()
            print("Фронтенд сервер остановлен.")

        if bot_process and bot_process.poll() is None:
            bot_process.terminate()
            print("Telegram бот остановлен.")

# === ТОЧКА ВХОДА ===
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Завершение работы...")