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
    <div v-else-if="userStore.userData" class="w-full max-w-4xl bg-gray-800 shadow-lg rounded-lg overflow-hidden p-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- ID -->
        <div class="flex flex-col">
          <span class="text-gray-500 text-sm">ID</span>
          <span class="text-gray-300">{{ userStore.userData.id }}</span>
        </div>

        <!-- Telegram ID -->
        <div class="flex flex-col">
          <span class="text-gray-500 text-sm">Telegram ID</span>
          <span class="text-gray-300">{{ userStore.userData.telegram_id }}</span>
        </div>

        <!-- Имя пользователя -->
        <div class="flex flex-col">
          <span class="text-gray-500 text-sm">Имя пользователя</span>
          <span class="text-gray-300">{{ userStore.userData.username || '-' }}</span>
        </div>

        <!-- Имя -->
        <div class="flex flex-col">
          <span class="text-gray-500 text-sm">Имя</span>
          <span class="text-gray-300">{{ userStore.userData.first_name || '-' }}</span>
        </div>

        <!-- Фамилия -->
        <div class="flex flex-col">
          <span class="text-gray-500 text-sm">Фамилия</span>
          <span class="text-gray-300">{{ userStore.userData.last_name || '-' }}</span>
        </div>

        <!-- Администратор -->
        <div class="flex flex-col">
          <span class="text-gray-500 text-sm">Администратор</span>
          <span class="text-gray-300">{{ userStore.userData.is_admin ? 'Да' : 'Нет' }}</span>
        </div>

        <!-- Дата регистрации -->
        <div class="flex flex-col">
          <span class="text-gray-500 text-sm">Дата регистрации</span>
          <span class="text-gray-300">{{ formatDate(userStore.userData.created_at) }}</span>
        </div>

        <!-- Последнее обновление -->
        <div class="flex flex-col">
          <span class="text-gray-500 text-sm">Последнее обновление</span>
          <span class="text-gray-300">{{ formatDate(userStore.userData.updated_at) }}</span>
        </div>
      </div>
    </div>

    <!-- Если данных нет -->
    <div v-else class="text-gray-400">
      Нет данных для отображения.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/userStore.ts';

// Инициализируем хранилище
const userStore = useUserStore();

// Состояние для загрузки данных
const isLoading = ref(true);

// Функция для загрузки данных пользователя
onMounted(async () => {
  try {
    // Попытка загрузить данные пользователя
    if (!userStore.userData) {
      await userStore.loadUserData();
    }
  } catch (error) {
    console.error('Ошибка:', error.message);
  } finally {
    isLoading.value = false; // Завершаем загрузку
  }
});

/**
 * Преобразует дату в удобочитаемый формат.
 * @param dateStr - Дата в строковом формате.
 * @returns Отформатированная дата или '-' если дата отсутствует.
 */
const formatDate = (dateStr: string | null): string => {
  if (!dateStr) return '-';
  const date = new Date(dateStr);
  return date.toLocaleString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};
</script>