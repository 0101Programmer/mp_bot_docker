// 1. Группа сборки по умолчанию (запускается при `docker buildx bake`)
group "default" {
    targets = ["web", "frontend"]  // Порядок важен - собирается последовательно
}

// 2. Настройки для backend-образа
target "web" {
    context = "."  // Сборка из текущей директории
    dockerfile = "./Dockerfile"  // Путь относительно context
    tags = ["mp_bot_docker-web:latest"]
}

// 3. Настройки для frontend-образа
target "frontend" {
    context = "./mp-bot-docker-frontend"  // Отдельная папка с фронтом
    dockerfile = "./Dockerfile"
    tags = ["mp_bot_docker-frontend:latest"]
}
