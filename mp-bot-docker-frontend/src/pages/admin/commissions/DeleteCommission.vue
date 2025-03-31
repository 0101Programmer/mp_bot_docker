<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-4">
    <!-- Приветственное сообщение -->
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Удалить комиссию
    </h1>

    <!-- Блок для отображения ошибок -->
    <div v-if="errorMessage" class="w-full max-w-2xl bg-red-800 text-white rounded-lg p-4 mb-4">
      <p class="text-sm">{{ errorMessage }}</p>
    </div>

    <!-- Форма для удаления комиссии -->
    <form @submit.prevent="deleteCommission" class="w-full max-w-2xl bg-gray-800 shadow-lg rounded-lg overflow-hidden p-6">
      <!-- Выбор комиссии из выпадающего списка -->
      <div class="mb-4">
        <label for="commission_select" class="block text-sm font-medium text-gray-300">Выберите комиссию</label>
        <select
          id="commission_select"
          v-model="selectedCommissionId"
          class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="" disabled selected>Выберите комиссию</option>
          <option v-for="commission in commissions" :key="commission.id" :value="commission.id">
            {{ commission.name }}
          </option>
        </select>
      </div>

      <!-- Ввод ID комиссии -->
      <div class="mb-4">
        <label for="commission_id" class="block text-sm font-medium text-gray-300">Или введите ID комиссии</label>
        <input
          id="commission_id"
          v-model="manualCommissionId"
          type="number"
          class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Введите ID комиссии"
        />
      </div>

      <!-- Кнопка удаления -->
      <button
        type="submit"
        :disabled="isLoading"
        class="w-full px-4 py-2 bg-red-500 text-white font-semibold rounded-md hover:bg-red-600 transition-colors duration-200 disabled:bg-gray-500"
      >
        {{ isLoading ? 'Удаление...' : 'Удалить комиссию' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import {useUserStore} from "../../../stores/userStore.ts";

// Инициализируем роутер и хранилище пользователя
const router = useRouter();
const userStore = useUserStore();

// Состояния для полей формы
const commissions = ref<{ id: string; name: string }[]>([]);
const selectedCommissionId = ref<string | null>(null);
const manualCommissionId = ref<string>('');
const errorMessage = ref<string>('');
const isLoading = ref(false);

// Загрузка списка комиссий
onMounted(async () => {
  try {
    const response = await fetch('http://localhost:8000/telegram_bot/commissions/');
    if (response.ok) {
      commissions.value = await response.json();
    } else {
      console.error('Ошибка при загрузке комиссий');
    }
  } catch (error) {
    console.error('Ошибка сети:', error);
  }
});

// Функция для удаления комиссии
const deleteCommission = async () => {
  errorMessage.value = '';
  isLoading.value = true;

  // Определяем ID комиссии: из выпадающего списка или вручную введенный
  const commissionId = selectedCommissionId.value || manualCommissionId.value;
  if (!commissionId) {
    errorMessage.value = 'Пожалуйста, выберите комиссию или введите её ID.';
    isLoading.value = false;
    return;
  }

  try {
    const response = await fetch(`http://localhost:8000/telegram_bot/delete_commission/${commissionId}/`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userStore.userData?.user_id, // Передаем user_id из хранилища
      }),
    });

    if (response.ok) {
      alert('Комиссия успешно удалена!');
      await router.push('/admin_panel'); // Перенаправляем на панель администратора
    } else {
      // Обработка ошибок на основе статуса ответа
      const errorData = await response.json();
      if (response.status === 404) {
        errorMessage.value = 'Комиссия с указанным ID не найдена.';
      } else {
        errorMessage.value = errorData.message || 'Произошла ошибка при удалении комиссии.';
      }
    }
  } catch (error) {
    console.error('Ошибка:', error.message);
    errorMessage.value = `Ошибка при удалении комиссии: ${error.message}`;
  } finally {
    isLoading.value = false;
  }
};
</script>