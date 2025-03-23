import subprocess
import sys
import asyncio

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

        # Ждём завершения процесса
        process.wait()

        # Проверяем код завершения
        if process.returncode != 0:
            print(f"Команда завершилась с ошибкой: {' '.join(command)}")
            sys.exit(process.returncode)

    except Exception as e:
        print(f"Ошибка при выполнении команды: {e}")
        sys.exit(1)

# === ОСНОВНАЯ ФУНКЦИЯ ===
async def main():
    try:
        # Запускаем Django сервер
        print("Запуск Django сервера...")
        django_server = subprocess.Popen(
            ["python", "manage.py", "runserver"],
        )

        # Запускаем бота
        run_command(["python", "manage.py", "runbot"])

        # Ждём завершения процессов
        django_server.wait()

    except KeyboardInterrupt:
        print("Процесс прерван пользователем.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        # Убиваем процессы, если они ещё работают
        if django_server.poll() is None:
            django_server.terminate()
            print("Django сервер остановлен.")

# === ТОЧКА ВХОДА ===
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Завершение работы...")