<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from './stores/userStore';

// Инициализируем хранилище и роутер
const userStore = useUserStore();
const route = useRoute();
const router = useRouter();

// Функция для проверки, нужно ли показывать навбар
const shouldShowNavbar = computed(() => {
  const excludedPaths = ['/success', '/error', '/']; // Список путей, где навбар не нужен
  return !excludedPaths.includes(route.path);
});

// Функция для выхода
const logout = async () => {
  try {
    // Получаем telegram_id из хранилища
    const telegramId = userStore.userData?.telegram_id;
    if (!telegramId) {
      throw new Error('Telegram ID не найден.');
    }

    // Отправляем запрос на выход с query-параметром
    const response = await fetch(`http://localhost:8000/telegram_bot/logout/?telegram_id=${telegramId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Ошибка при выходе.');
    }

    // Получаем данные из ответа
    const data = await response.json();

    // Очищаем данные пользователя в хранилище
    userStore.clearUserData();

    // Перенаправляем на страницу успеха с сообщением
    await router.push(`/success?message=${encodeURIComponent(data.message)}`);
  } catch (error) {
    console.error('Ошибка:', error.message);
    alert(`Ошибка при выходе: ${error.message}`);
  }
};
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white">
    <!-- Навигационное меню -->
    <nav v-if="shouldShowNavbar" class="bg-gray-800 shadow-md p-4">
      <div class="container mx-auto flex justify-between items-center">
        <!-- Логотип -->
        <div class="text-lg font-bold text-blue-400">MP BOT DOCKER</div>

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
        </ul>

        <!-- Кнопка выхода -->
        <button
          @click="logout"
          class="text-red-500 hover:text-red-400 transition-colors duration-200"
        >
          Выйти
        </button>
      </div>
    </nav>

    <!-- Основной контент -->
    <router-view></router-view>
  </div>
</template>