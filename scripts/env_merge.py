import os

def merge_env_files(env_folder=".env_collection", output_file=".env"):
    """
    Объединяет все .env файлы из папки env_folder в один файл output_file,
    игнорируя комментарии и пустые строки.
    """
    # Получаем список всех .env файлов в папке
    try:
        env_files = [
            f for f in os.listdir(env_folder)
            if f.endswith(".env") and os.path.isfile(os.path.join(env_folder, f))
        ]
    except FileNotFoundError:
        print(f"Папка '{env_folder}' не найдена.")
        return

    if not env_files:
        print(f"В папке '{env_folder}' нет файлов с расширением .env.")
        return

    # Открываем выходной файл для записи
    with open(output_file, "w", encoding="utf-8") as outfile:
        for env_file in env_files:
            file_path = os.path.join(env_folder, env_file)
            print(f"Обрабатываю файл: {file_path}")
            try:
                # Открываем каждый файл с явным указанием кодировки UTF-8
                with open(file_path, "r", encoding="utf-8") as infile:
                    # Копируем только непустые строки, которые не являются комментариями
                    for line in infile:
                        stripped_line = line.strip()
                        if stripped_line and not stripped_line.startswith("#"):
                            outfile.write(stripped_line + "\n")
            except UnicodeDecodeError as e:
                print(f"Ошибка при чтении файла {file_path}: {e}")

    print(f"Все файлы успешно объединены в '{output_file}'.")

if __name__ == "__main__":
    # Укажите папку с .env файлами и выходной файл
    merge_env_files(env_folder=".env_collection", output_file=".env")