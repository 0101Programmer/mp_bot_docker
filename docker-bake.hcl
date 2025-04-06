group "default" {
    targets = ["web", "bot", "frontend"]
}

target "web" {
    context = "."
    dockerfile = "./Dockerfile"
    tags = ["mp_bot_docker-web"]
}

target "bot" {
    context = "."
    dockerfile = "./Dockerfile"
    tags = ["mp_bot_docker-bot"]
}

target "frontend" {
    context = "./mp-bot-docker-frontend"
    dockerfile = "./Dockerfile"
    tags = ["mp_bot_docker-frontend"]
}