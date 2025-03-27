<script setup lang="ts">
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <div class="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
    <h1 class="text-4xl font-bold text-blue-600 mb-6">Vite + Vue + TailwindCSS</h1>

    <div class="flex space-x-4">
      <a href="https://vite.dev" target="_blank" class="hover:scale-110 transition-transform">
        <img src="/vite.svg" alt="Vite logo" class="w-24 h-24 rounded-full shadow-lg" />
      </a>
      <a href="https://vuejs.org/" target="_blank" class="hover:scale-110 transition-transform">
        <img src="./assets/vue.svg" alt="Vue logo" class="w-24 h-24 rounded-full shadow-lg" />
      </a>
    </div>

    <HelloWorld msg="Vite + Vue" />
  </div>
</template>
