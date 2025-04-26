import subprocess
import re
import os
import sys
import time
from pathlib import Path


def find_project_root(start_path):
    current_path = Path(start_path).absolute()
    while current_path != current_path.parent:
        if (current_path / ".env").exists():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError("Не удалось найти .env файл")


def update_env_file(env_path, tunnel_url):
    try:
        with open(env_path, 'r') as f:
            content = f.read()

        content = re.sub(r'TELEGRAM_WEBAPP_HOST=.*', f'TELEGRAM_WEBAPP_HOST={tunnel_url}', content)
        content = re.sub(r'VITE_TELEGRAM_WEBAPP_HOST=.*', f'VITE_TELEGRAM_WEBAPP_HOST={tunnel_url}', content)
        content = re.sub(r'TELEGRAM_WEBAPP_HOST_FOR_CORS=https://.*',
                         f'TELEGRAM_WEBAPP_HOST_FOR_CORS=https://{tunnel_url}', content)

        with open(env_path, 'w') as f:
            f.write(content)

        print(f"Обновлен .env файл с новым URL: {tunnel_url}")
        return True
    except Exception as e:
        print(f"Ошибка при обновлении .env файла: {e}")
        return False


def run_cloudflared_tunnel(cloudflared_path, project_root):
    os.chdir(project_root)

    # Запускаем процесс в фоновом режиме (без ожидания завершения)
    process = subprocess.Popen(
        [cloudflared_path, 'tunnel', '--url', 'http://localhost:5173'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    print("Cloudflared tunnel запущен...")
    tunnel_url = None
    start_time = time.time()
    timeout = 30  # Максимальное время ожидания URL

    while time.time() - start_time < timeout:
        line = process.stderr.readline()
        if not line:
            time.sleep(0.1)
            continue

        print(line.strip())

        # Ищем URL туннеля
        match = re.search(r'https://([a-zA-Z0-9-]+\.trycloudflare\.com)', line)
        if match:
            tunnel_url = match.group(1)
            print(f"Найден URL туннеля: {tunnel_url}")
            if update_env_file(project_root / ".env", tunnel_url):
                # Возвращаем PID процесса вместо его завершения
                return process.pid

    # Если время вышло
    process.terminate()
    return None


if __name__ == "__main__":
    try:
        SCRIPT_DIR = Path(__file__).parent.absolute()
        PROJECT_ROOT = find_project_root(SCRIPT_DIR)
        CLOUDFLARED_PATH = r"C:\cloudflared\cloudflared.exe"

        print("Запуск cloudflared tunnel...")
        pid = run_cloudflared_tunnel(CLOUDFLARED_PATH, PROJECT_ROOT)

        if pid is None:
            print("Не удалось получить URL туннеля или обновить .env файл")
            sys.exit(1)

        print(f"Туннель успешно запущен (PID: {pid}), .env обновлен")
        print("Этот скрипт завершает работу, но туннель продолжает работать в фоне")
        sys.exit(0)  # Успешное завершение

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        sys.exit(1)