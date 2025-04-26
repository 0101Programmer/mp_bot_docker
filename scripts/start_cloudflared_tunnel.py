import subprocess
import re
import os
from pathlib import Path


def find_project_root(start_path):
    """Ищет корень проекта по наличию .env файла, поднимаясь вверх по директориям"""
    current_path = Path(start_path).absolute()

    while current_path != current_path.parent:  # Пока не достигли корня диска
        if (current_path / ".env").exists():
            return current_path
        current_path = current_path.parent

    raise FileNotFoundError("Не удалось найти .env файл в родительских директориях")


def update_env_file(env_path, tunnel_url):
    """Обновляет .env файл с новым URL туннеля"""
    # Читаем содержимое файла
    with open(env_path, 'r') as f:
        content = f.read()

    # Обновляем значения
    content = re.sub(
        r'TELEGRAM_WEBAPP_HOST=.*',
        f'TELEGRAM_WEBAPP_HOST={tunnel_url}',
        content
    )
    content = re.sub(
        r'VITE_TELEGRAM_WEBAPP_HOST=.*',
        f'VITE_TELEGRAM_WEBAPP_HOST={tunnel_url}',
        content
    )
    content = re.sub(
        r'TELEGRAM_WEBAPP_HOST_FOR_CORS=https://.*',
        f'TELEGRAM_WEBAPP_HOST_FOR_CORS=https://{tunnel_url}',
        content
    )

    # Записываем обратно
    with open(env_path, 'w') as f:
        f.write(content)

    print(f"Обновлен .env файл с новым URL: {tunnel_url}")


def run_cloudflared_tunnel(cloudflared_path, project_root):
    """Запускает cloudflared tunnel и извлекает URL"""
    os.chdir(project_root)

    # Запускаем процесс
    process = subprocess.Popen(
        [cloudflared_path, 'tunnel', '--url', 'http://localhost:5173'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    print("Cloudflared tunnel запущен...")

    # Читаем вывод в реальном времени и ищем URL
    tunnel_url = None
    while True:
        line = process.stderr.readline()
        if not line:
            break

        print(line.strip())  # Выводим логи

        # Ищем URL туннеля в выводе
        match = re.search(r'https://([a-zA-Z0-9-]+\.trycloudflare\.com)', line)
        if match:
            tunnel_url = match.group(1)
            print(f"Найден URL туннеля: {tunnel_url}")
            update_env_file(project_root / ".env", tunnel_url)

    return process


if __name__ == "__main__":
    # Определяем пути автоматически
    SCRIPT_DIR = Path(__file__).parent.absolute()
    PROJECT_ROOT = find_project_root(SCRIPT_DIR)
    CLOUDFLARED_PATH = r"C:\cloudflared\cloudflared.exe"

    print(f"Корень проекта: {PROJECT_ROOT}")
    print("Запуск cloudflared tunnel...")

    process = run_cloudflared_tunnel(CLOUDFLARED_PATH, PROJECT_ROOT)

    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nОстановка cloudflared tunnel...")
        process.terminate()