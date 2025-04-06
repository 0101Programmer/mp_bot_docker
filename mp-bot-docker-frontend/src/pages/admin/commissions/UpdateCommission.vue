<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-4">
    <!-- Приветственное сообщение -->
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Редактировать комиссию
    </h1>

    <!-- Блок для отображения ошибок -->
    <div v-if="errorMessage" class="w-full max-w-2xl bg-red-800 text-white rounded-lg p-4 mb-4">
      <p class="text-sm">{{ errorMessage }}</p>
    </div>

    <!-- Форма для редактирования комиссии -->
    <form
      v-if="isCommissionFound"
      @submit.prevent="updateCommission"
      class="w-full max-w-2xl bg-gray-800 shadow-lg rounded-lg overflow-hidden p-6"
    >
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
        ></textarea>
      </div>

      <!-- Кнопка сохранения изменений -->
      <button
        type="submit"
        :disabled="isLoading"
        class="w-full px-4 py-2 bg-green-500 text-white font-semibold rounded-md hover:bg-green-600 transition-colors duration-200 disabled:bg-gray-500"
      >
        {{ isLoading ? 'Сохранение...' : 'Сохранить изменения' }}
      </button>
    </form>

    <!-- Сообщение, если комиссия не найдена -->
    <div v-else class="w-full max-w-2xl bg-gray-800 shadow-lg rounded-lg overflow-hidden p-6 text-center">
      <p class="text-gray-400 text-lg mb-4">
        Комиссия с указанным ID не найдена.
      </p>
      <p class="text-gray-500 text-sm">
        Пожалуйста,
        <a href="/admin_panel" class="text-blue-400 underline hover:text-blue-500 transition-colors duration-200">
          вернитесь на панель администратора
        </a>
        и выберите другую комиссию.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/userStore.ts';
import { useConfigStore } from '@/stores/configStore'; // Импортируем configStore

// Инициализируем роутер, текущий маршрут, хранилище пользователя и хранилище конфигурации
const router = useRouter();
const route = useRoute();
const userStore = useUserStore();
const configStore = useConfigStore(); // Инициализируем configStore

// Получаем ID комиссии из параметров маршрута
const commissionId = route.params.id; // ID комиссии

// Состояния для полей формы
const name = ref('');
const description = ref('');
const errorMessage = ref<string>('');
const isLoading = ref(false);
const isCommissionFound = ref(true); // Флаг, найдена ли комиссия

// Загрузка данных комиссии
onMounted(async () => {
  try {
    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/service/commission_detail/${commissionId}/`);
    if (response.ok) {
      const data = await response.json();
      name.value = data.name;
      description.value = data.description;
    } else {
      console.error('Ошибка при загрузке данных комиссии');
      isCommissionFound.value = false; // Комиссия не найдена
      errorMessage.value = 'Комиссия с указанным ID не найдена.';
    }
  } catch (error) {
    console.error('Ошибка сети:', error);
    isCommissionFound.value = false; // Комиссия не найдена
    errorMessage.value = 'Произошла ошибка при загрузке данных комиссии.';
  }
});

// Функция для обновления комиссии
const updateCommission = async () => {
  errorMessage.value = '';
  isLoading.value = true;

  try {
    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/admin/update_commission/${commissionId}/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userStore.userData?.user_id, // Передаем user_id из хранилища
        name: name.value,
        description: description.value,
      }),
    });

    if (response.ok) {
      alert('Комиссия успешно обновлена!');
      await router.push('/admin_panel'); // Перенаправляем на панель администратора
    } else {
      const errorData = await response.json();
      if (errorData.name || errorData.description) {
        // Если есть ошибки валидации, выводим их
        errorMessage.value = [
          ...(errorData.name || []),
          ...(errorData.description || []),
        ].join(' ');
      } else {
        // В противном случае выводим общее сообщение
        errorMessage.value = errorData.message || 'Произошла ошибка при обновлении комиссии.';
      }
    }
  } catch (error) {
    console.error('Ошибка:', error.message);
    errorMessage.value = `Ошибка при обновлении комиссии: ${error.message}`;
  } finally {
    isLoading.value = false;
  }
};
</script>