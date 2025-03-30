<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUserStore } from '../stores/userStore';
import { useRouter } from 'vue-router';

// Инициализируем хранилище и роутер
const userStore = useUserStore();
const router = useRouter();

// Состояние для загрузки данных
const isLoading = ref(true);

// Функция для загрузки данных пользователя
onMounted(async () => {
  try {
    // Если токена нет, перенаправляем на страницу ошибки
    if (!userStore.authToken) {
      throw new Error('Токен отсутствует. Пожалуйста, авторизуйтесь.');
    }

    // Если данные пользователя отсутствуют, загружаем их
    if (!userStore.userData) {
      await userStore.loadUserData();
    }
  } catch (error) {
    console.error('Ошибка:', error.message);
    await router.push(`/error?message=${encodeURIComponent(error.message)}`);
  } finally {
    isLoading.value = false; // Завершаем загрузку
  }
});
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-4">
    <!-- Приветственное сообщение -->
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Личный кабинет
    </h1>

    <!-- Если данные загружаются -->
    <div v-if="isLoading" class="text-gray-400">
      Загрузка данных...
    </div>

    <!-- Если данные загружены -->
    <div v-else-if="userStore.userData" class="w-full max-w-4xl bg-gray-800 shadow-lg rounded-lg overflow-hidden">
      <table class="w-full text-sm text-left text-gray-400">
        <!-- Заголовок таблицы -->
        <thead class="text-xs uppercase bg-gray-700 text-gray-300">
          <tr>
            <th scope="col" class="px-6 py-3">ID</th>
            <th scope="col" class="px-6 py-3">Telegram ID</th>
            <th scope="col" class="px-6 py-3">Имя пользователя</th>
            <th scope="col" class="px-6 py-3">Имя</th>
            <th scope="col" class="px-6 py-3">Фамилия</th>
            <th scope="col" class="px-6 py-3">Администратор</th>
          </tr>
        </thead>

        <!-- Тело таблицы -->
        <tbody>
          <tr class="border-b border-gray-700 hover:bg-gray-700">
            <td class="px-6 py-4">{{ userStore.userData.user_id }}</td>
            <td class="px-6 py-4">{{ userStore.userData.telegram_id }}</td>
            <td class="px-6 py-4">{{ userStore.userData.username || '-' }}</td>
            <td class="px-6 py-4">{{ userStore.userData.first_name || '-' }}</td>
            <td class="px-6 py-4">{{ userStore.userData.last_name || '-' }}</td>
            <td class="px-6 py-4">{{ userStore.userData.is_admin ? 'Да' : 'Нет' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Если данных нет -->
    <div v-else class="text-gray-400">
      Нет данных для отображения.
    </div>
  </div>
</template>