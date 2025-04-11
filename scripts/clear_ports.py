import os
import subprocess
import re
import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

def find_and_kill_processes(ports):
    """
    Ищет процессы, занимающие указанные порты, и завершает их.
    :param ports: Список портов для проверки (например, [8000, 5173]).
    """
    for port in ports:
        try:
            # Выполняем команду netstat для поиска процессов на указанном порту
            result = subprocess.run(
                ["netstat", "-ano"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            if result.returncode != 0:
                logging.error(f"Ошибка при выполнении netstat: {result.stderr}")
                continue

            # Регулярное выражение для поиска строки с указанным портом
            pattern = re.compile(rf"TCP\s+.*:{port}\s+.*LISTENING\s+(\d+)")
            matches = pattern.findall(result.stdout)

            if not matches:
                logging.info(f"Порт {port} не занят.")
                continue

            # Завершаем все найденные процессы
            for pid in matches:
                try:
                    logging.info(f"Завершение процесса с PID={pid} на порту {port}.")
                    subprocess.run(
                        ["taskkill", "/PID", pid, "/F"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                except Exception as e:
                    logging.error(f"Ошибка при завершении процесса с PID={pid}: {e}")

        except Exception as e:
            logging.error(f"Произошла ошибка при обработке порта {port}: {e}")

if __name__ == "__main__":
    # Список портов для очистки
    ports_to_clear = [8000, 5173]

    logging.info("Начинаем очистку портов...")
    find_and_kill_processes(ports_to_clear)
    logging.info("Очистка портов завершена.")