<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';

// Инициализируем route
const route = useRoute();

// Получаем сообщение из query-параметров
const message = ref(route.query.message || 'Вы успешно вышли из системы.');
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
    <!-- Сообщение об успехе -->
    <h1 class="text-3xl font-bold text-green-500 mt-8 mb-6 text-center">
      Успех!
    </h1>

    <!-- Текст сообщения -->
    <p class="text-gray-400 text-center">{{ message }}</p>
  </div>
</template>