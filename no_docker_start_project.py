import asyncio
import subprocess
import sys
import time
from decouple import config


def run_command(command, check=False):
    """Запускает команду с возможностью проверки успешности"""
    try:
        if check:
            subprocess.run(command, text=True, encoding="utf-8", errors="replace", check=True)
            return None
        return subprocess.Popen(
            command,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
    except Exception as e:
        print(f"Ошибка при выполнении команды: {' '.join(command)} - {e}")
        sys.exit(1)


async def main():
    processes = {
        'django': None,
        'frontend': None,
        'bot': None
    }

    try:
        print("Запуск всех компонентов...")

        # 1. Запускаем Cloudflare Tunnel (неблокирующий вызов)
        print("Запуск Cloudflare Tunnel...")
        tunnel_process = subprocess.Popen(
            ["python", "scripts/start_cloudflared_tunnel.py"],
            text=True,
            encoding="utf-8"
        )

        # Ждем завершения скрипта (но сам туннель продолжит работать)
        tunnel_process.wait()
        if tunnel_process.returncode != 0:
            print("Ошибка при запуске Cloudflare Tunnel")
            sys.exit(1)

        # Остальные компоненты
        print("Запуск Django сервера...")
        processes['django'] = subprocess.Popen(["python", "manage.py", "runserver"])

        print("Проверка Redis...")
        subprocess.run(["python", "manage.py", "checkredis"], check=True)

        print("Запуск фронтенда...")
        processes['frontend'] = subprocess.Popen(
            ["cmd", "/c", "cd", "mp-bot-docker-frontend", "&&", "npm", "run", "dev"]
        )

        print("Запуск Telegram бота...")
        processes['bot'] = subprocess.Popen(["python", "manage.py", "runbot"])

        print("Все компоненты успешно запущены. Нажмите Ctrl+C для завершения.")
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\nЗавершение работы...")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка: {e}")
    finally:
        # Завершаем только наши процессы (не трогаем cloudflared)
        for name in ['bot', 'frontend', 'django']:
            if processes[name] and processes[name].poll() is None:
                processes[name].terminate()
                try:
                    processes[name].wait(timeout=5)
                except subprocess.TimeoutExpired:
                    processes[name].kill()
        print("Примечание: Cloudflare Tunnel продолжает работать в фоне")


if __name__ == "__main__":
    USE_DOCKER = config("USE_DOCKER", default="0")

    if USE_DOCKER == "1":
        print("Флаг USE_DOCKER установлен в 1. Используется конфигурация с Docker.")
        sys.exit(1)

    asyncio.run(main())