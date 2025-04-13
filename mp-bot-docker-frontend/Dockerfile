FROM node:23-alpine

# Установка рабочей директории
WORKDIR /app

# Копирование package.json и package-lock.json
COPY package*.json ./

# Установка зависимостей
RUN npm install

# Копирование исходного кода приложения
COPY . .

# Открытие порта для Vite Dev Server
EXPOSE 5173

# Запуск Vite Dev Server
CMD ["npm", "run", "dev"]