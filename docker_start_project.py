import subprocess
from decouple import config


def run_command(command, description):
    """Выполняет команду и выводит описание."""
    print(f"=== {description} ===")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"Ошибка при выполнении команды: {command}")
        exit(1)


def check_images_exist():
    """
    Проверяет, существуют ли локально образы, указанные в docker-compose.yml.
    Возвращает True, если все образы найдены, и False в противном случае.
    """
    try:
        # Получаем список образов из docker-compose.yml
        result = subprocess.run(
            "docker compose images --quiet",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print("Образы не найдены или произошла ошибка при проверке.")
            return False

        # Если есть вывод, значит образы существуют
        return bool(result.stdout.strip())
    except Exception as e:
        print(f"Ошибка при проверке образов: {e}")
        return False


if __name__ == "__main__":
    # Загружаем значение USE_DOCKER из .env
    USE_DOCKER = config("USE_DOCKER")

    # Проверка, что USE_DOCKER=1
    if USE_DOCKER != "1":
        print("Флаг USE_DOCKER не установлен в 1. Сейчас настроена конфигурация для запуска проекта без Docker.")
        exit(1)

    try:
        # Проверяем наличие образов
        if not check_images_exist():
            print("Локальные образы не найдены. Выполняется сборка образов...")
            run_command("docker buildx bake", "Сборка образов через docker buildx bake")

        # Запуск контейнеров
        run_command("docker compose up", "Запуск контейнеров через docker compose up")

    except KeyboardInterrupt:
        print("\nПроцесс прерван пользователем.")