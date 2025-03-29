<script setup lang="ts">
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white">
    <!-- Навигационное меню -->
    <nav class="bg-gray-800 shadow-md p-4">
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
              to="/settings"
              class="text-blue-400 hover:text-blue-300 transition-colors duration-200"
            >
              Настройки
            </router-link>
          </li>
        </ul>

        <!-- Кнопка выхода -->
        <button class="text-red-500 hover:text-red-400 transition-colors duration-200">
          Выйти
        </button>
      </div>
    </nav>

    <!-- Основной контент -->
    <router-view></router-view>
  </div>
</template>
