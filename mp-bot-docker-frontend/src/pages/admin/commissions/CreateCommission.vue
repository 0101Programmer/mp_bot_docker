<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-4">
    <!-- Приветственное сообщение -->
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Создать комиссию
    </h1>

    <!-- Блок для отображения ошибок -->
    <div v-if="Object.keys(errors).length > 0" class="w-full max-w-2xl bg-red-800 text-white rounded-lg p-4 mb-4">
      <h2 class="text-lg font-bold mb-2">Ошибки валидации:</h2>
      <ul class="text-sm whitespace-pre-wrap break-words">
        <li v-for="(error, field) in errors" :key="field">
          {{ field }}: {{ error.join(', ') }}
        </li>
      </ul>
    </div>

    <!-- Форма для создания комиссии -->
    <form @submit.prevent="createCommission" class="w-full max-w-2xl bg-gray-800 shadow-lg rounded-lg overflow-hidden p-6">
      <!-- Поле для названия комиссии -->
      <div class="mb-4">
        <label for="commission_name" class="block text-sm font-medium text-gray-300">Название комиссии</label>
        <input
          id="commission_name"
          v-model="name"
          type="text"
          class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Введите название комиссии"
          required
        />
      </div>

      <!-- Поле для описания комиссии -->
      <div class="mb-4">
        <label for="commission_description" class="block text-sm font-medium text-gray-300">Описание комиссии</label>
        <textarea
          id="commission_description"
          v-model="description"
          rows="5"
          class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Введите описание комиссии"
          required
        ></textarea>
      </div>

      <!-- Кнопка отправки -->
      <button
        type="submit"
        :disabled="isLoading"
        class="w-full px-4 py-2 bg-blue-500 text-white font-semibold rounded-md hover:bg-blue-600 transition-colors duration-200 disabled:bg-gray-500"
      >
        {{ isLoading ? 'Создание...' : 'Создать комиссию' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore.ts';
import { useConfigStore } from '@/stores/configStore'; // Импортируем configStore

// Инициализируем роутер, хранилище пользователя и хранилище конфигурации
const router = useRouter();
const userStore = useUserStore();
const configStore = useConfigStore(); // Инициализируем configStore

// Состояния для полей формы
const name = ref('');
const description = ref('');
const errors = ref<any>({});
const isLoading = ref(false);

// Функция для создания комиссии
const createCommission = async () => {
  errors.value = {};
  isLoading.value = true;

  try {
    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/admin/create_commission/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userStore.userData?.user_id, // Передаем user_id из хранилища
        name: name.value,
        description: description.value,
      }),
    });

    if (response.ok) {
      alert('Комиссия успешно создана!');
      await router.push('/admin_panel'); // Перенаправляем на панель администратора
    } else {
      errors.value = await response.json(); // Отображаем ошибки валидации
    }
  } catch (error) {
    console.error('Ошибка:', error.message);
    alert(`Ошибка при создании комиссии: ${error.message}`);
  } finally {
    isLoading.value = false;
  }
};
</script>