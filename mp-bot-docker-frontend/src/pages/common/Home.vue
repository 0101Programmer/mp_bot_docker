<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUserStore } from '@/stores/userStore.ts';
import { useRouter } from 'vue-router';

// Инициализируем хранилище и роутер
const userStore = useUserStore();
const router = useRouter();

// Состояние для загрузки данных
const isLoading = ref(true);

// Функция для загрузки данных через API
onMounted(() => {
  const token = new URLSearchParams(window.location.search).get('token'); // Получаем токен из URL

  if (!token) {
    console.error('Токен не найден в URL.');
    router.push('/error?message=Токен отсутствует');
    isLoading.value = false;
    return;
  }

  // Сохраняем токен в localStorage и загружаем данные пользователя
  localStorage.setItem('authToken', token);
  userStore.setAuthToken(token);
  userStore.loadUserData().finally(() => {
    isLoading.value = false;
    router.push('/account');
  });
});
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
    <!-- Приветственное сообщение -->
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Загрузка данных...
    </h1>

    <!-- Индикатор загрузки -->
    <div v-if="isLoading" class="text-gray-400">
      Загрузка данных...
    </div>

    <!-- Если произошла ошибка -->
    <div v-else class="text-red-500">
      Произошла ошибка. Пожалуйста, попробуйте снова.
    </div>
  </div>
</template>