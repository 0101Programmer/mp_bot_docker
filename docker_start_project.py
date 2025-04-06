import subprocess
from decouple import config


def run_command(command, description):
    """Выполняет команду и выводит описание."""
    print(f"=== {description} ===")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Ошибка при выполнении команды: {command}")
        exit(1)


if __name__ == "__main__":
    # Загружаем значение USE_DOCKER из .env
    USE_DOCKER = config("USE_DOCKER")

    # Обратная проверка: если USE_DOCKER=0, выводим сообщение об ошибке
    if USE_DOCKER != "1":
        print("Флаг USE_DOCKER не установлен в 1. Сейчас настроена конфигурация для запуска без Docker.")
        exit(1)

    try:
        # Сборка образов
        run_command("docker buildx bake", "Сборка образов через docker buildx bake")

        # Запуск контейнеров
        run_command("docker compose up", "Запуск контейнеров через docker compose up")

    except KeyboardInterrupt:
        print("\nПроцесс прерван пользователем.")