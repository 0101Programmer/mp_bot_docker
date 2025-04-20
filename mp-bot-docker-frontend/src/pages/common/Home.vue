<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';

onMounted(() => {
  const tg = window.Telegram?.WebApp;

  if (tg) {
    // Настраиваем интерфейс Telegram
    tg.expand();
    tg.setHeaderColor('#2a2a2a');
  }
});
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white p-4 flex flex-col items-center justify-center">
    <!-- Приветственное сообщение -->
    <h1 class="text-3xl font-bold text-blue-400 mb-6 text-center">
      Добро пожаловать!
    </h1>

    <!-- Кнопка в личный кабинет -->
    <a
      href="/account"
      class="inline-block px-6 py-3 bg-blue-500 rounded-lg text-lg font-medium hover:bg-blue-600 transition-colors"
    >
      В личный кабинет
    </a>
  </div>
</template>