<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore';
import { useConfigStore } from '@/stores/configStore';
import { useInitializeUserFromTelegram } from '@/composables/useInitializeUserFromTelegram';

// Инициализируем хранилище и роутер
const userStore = useUserStore();
const configStore = useConfigStore();
const route = useRoute();
const router = useRouter();

// Функция для проверки, нужно ли показывать навбар
const shouldShowNavbar = computed(() => {
  const excludedPaths = ['/success', '/error']; // Список путей, где навбар не нужен
  return !excludedPaths.includes(route.path);
});

// Вычисляемое свойство для имени пользователя
const username = computed(() => {
  return userStore.username || 'Гость'; // Если username отсутствует, показываем "Гость"
});

// Функция для проверки, нужно ли показывать приветствие
const shouldShowWelcome = computed(() => {
  return route.path === '/'; // Показываем приветствие только на главной странице
});

// Инициализация данных пользователя из Telegram WebApp
useInitializeUserFromTelegram();

// Загружаем данные пользователя после инициализации
onMounted(async () => {
  const currentTelegramId = userStore.telegramId;

  if (currentTelegramId) {
    await userStore.loadUserDataFromBackend(currentTelegramId); // Передаем telegramId
  } else {
    console.error('Telegram ID is not set or invalid.');
  }
});
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white">

    <!-- Навигационное меню -->
    <nav v-if="shouldShowNavbar" class="bg-gray-800 shadow-md p-4">
      <div class="container mx-auto flex justify-between items-center">
        <!-- Логотип -->
        <div class="text-lg font-bold text-blue-400">Youth Parliament Bot</div>

        <!-- Ссылки -->
        <ul class="flex space-x-4">
          <li>
            <router-link
              to="/account"
              class="text-blue-400 hover:text-blue-300 transition-colors duration-200"
            >
              Личный кабинет
            </router-link>
          </li>
          <li>
            <router-link
              to="/my_appeals"
              class="text-blue-400 hover:text-blue-300 transition-colors duration-200"
            >
              Мои обращения
            </router-link>
          </li>
          <li>
            <router-link
              to="/create_appeal"
              class="text-blue-400 hover:text-blue-300 transition-colors duration-200"
            >
              Написать обращение
            </router-link>
          </li>
          <li>
            <router-link
              to="/commissions_info"
              class="text-blue-400 hover:text-blue-300 transition-colors duration-200"
            >
              Информация о комиссиях
            </router-link>
          </li>
          <li>
            <router-link
              to="/admin_panel"
              class="text-blue-400 hover:text-blue-300 transition-colors duration-200"
            >
              Панель администратора
            </router-link>
          </li>
        </ul>
      </div>
    </nav>

    <!-- Приветствие -->
    <div v-if="shouldShowNavbar && shouldShowWelcome" class="container mx-auto p-4 text-center text-blue-400">
      Добро пожаловать, {{ username }}!
    </div>

    <!-- Основной контент -->
    <router-view></router-view>
  </div>
</template>