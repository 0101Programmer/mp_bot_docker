import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';
import dotenv from 'dotenv';

// Загружаем переменные окружения из .env файла в корне проекта
dotenv.config({ path: path.resolve(__dirname, '../.env') });

// https://vitejs.dev/config/
export default defineConfig({
  envDir: '../', // Указывает путь к директории с .env
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    allowedHosts: process.env.VITE_TELEGRAM_WEBAPP_HOST
      ? [process.env.VITE_TELEGRAM_WEBAPP_HOST]
      : [],
    proxy: {
      // Проксируем запросы к telegram-web-app.js
      '/telegram-web-app.js': {
        target: 'https://telegram.org/js/telegram-web-app.js',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/telegram-web-app\.js/, ''),
      },
    },
  },
  plugins: [
    vue(),
    tailwindcss(),
  ],
});