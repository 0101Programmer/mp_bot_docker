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
onMounted(async () => {
  try {
    const token = new URLSearchParams(window.location.search).get('token'); // Получаем токен из URL

    if (!token) {
      console.error('Токен не найден в URL.');
      await router.push('/error?message=Токен отсутствует');
      isLoading.value = false;
      return;
    }

    // Очищаем старые данные перед установкой новых
    userStore.clearUserData();

    // Сохраняем новый токен в localStorage и хранилище
    localStorage.setItem('authToken', token);
    userStore.setAuthToken(token);

    // Гарантируем, что loadUserData выполнится только после установки токена
    await userStore.loadUserData();

    // Переходим на страницу аккаунта
    await router.push('/account');
  } catch (error) {
    console.error('Ошибка при загрузке данных пользователя:', error);
    await router.push('/error?message=Ошибка при загрузке данных');
  } finally {
    isLoading.value = false;
  }
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