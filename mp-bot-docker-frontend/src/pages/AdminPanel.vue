<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-4">
    <!-- Приветственное сообщение -->
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Панель администратора
    </h1>

    <!-- Если пользователь администратор -->
    <div v-if="isAdmin" class="w-full max-w-2xl bg-gray-800 shadow-lg rounded-lg overflow-hidden p-6">
      <h2 class="text-xl font-bold text-blue-400 mb-4">Доступные действия:</h2>
      <ul class="space-y-3">
        <!-- Выпадающий список для действий с комиссиями -->
        <li>
          <details class="block w-full">
            <summary class="px-4 py-2 bg-gray-700 hover:bg-gray-800 text-white font-semibold rounded-md transition-colors duration-200 cursor-pointer">
              Действия с комиссиями
            </summary>
            <ul class="mt-2 space-y-2 pl-4">
              <li>
                <a href="/create_commission" class="block px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-md transition-colors duration-200">
                  Создать комиссию
                </a>
              </li>
              <li>
                <a href="/delete_commission" class="block px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-md transition-colors duration-200">
                  Удалить комиссию
                </a>
              </li>
              <li>
                <a href="#" class="block px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-md transition-colors duration-200">
                  Редактировать комиссию
                </a>
              </li>
            </ul>
          </details>
        </li>
        <li>
          <a href="#" class="block w-full px-4 py-2 bg-gray-700 hover:bg-gray-800 text-white font-semibold rounded-md transition-colors duration-200">
            Действия с пользователями
          </a>
        </li>
        <li>
          <a href="#" class="block w-full px-4 py-2 bg-gray-700 hover:bg-gray-800 text-white font-semibold rounded-md transition-colors duration-200">
            Просмотр обращений
          </a>
        </li>
        <li>
          <a href="#" class="block w-full px-4 py-2 bg-gray-700 hover:bg-gray-800 text-white font-semibold rounded-md transition-colors duration-200">
            Заявки на получение прав администратора
          </a>
        </li>
      </ul>
    </div>

    <!-- Если пользователь НЕ администратор -->
    <div v-else class="w-full max-w-2xl bg-gray-800 shadow-lg rounded-lg overflow-hidden p-6 text-center">
      <p class="text-gray-400 text-lg mb-4">
        У вас нет прав администратора.
      </p>
      <p class="text-gray-500 text-sm">
        Вы можете
        <a href="#" class="text-blue-400 underline hover:text-blue-500 transition-colors duration-200">
          заполнить форму
        </a>
        на получение прав администратора.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useUserStore } from '../stores/userStore';

// Инициализируем хранилище пользователя
const userStore = useUserStore();

// Проверка, является ли пользователь администратором
const isAdmin = computed(() => userStore.userData?.is_admin || false);
</script>