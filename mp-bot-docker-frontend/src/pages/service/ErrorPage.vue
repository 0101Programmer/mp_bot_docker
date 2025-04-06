<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
    <h1 class="text-3xl font-bold text-red-500 mb-4">Ошибка</h1>
    <p class="text-gray-400 text-center">{{ errorMessage }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const errorMessage = ref(decodeURIComponent(route.query.message as string));
</script>