<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-4">
    <!-- Приветственное сообщение -->
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Заявка на получение админ-прав
    </h1>

    <!-- Если данные загружаются -->
    <div v-if="isLoading" class="text-gray-400">
      Отправка данных...
    </div>

    <!-- Если пользователь уже администратор -->
    <div v-else-if="is_admin" class="text-gray-400">
      Ваша заявка была одобрена.
      <a href="/admin_panel" class="text-blue-500 hover:underline">Перейдите</a> на вкладку для администраторов или обновите приложение с главной страницы.
    </div>

    <!-- Если есть активная заявка -->
    <div v-else-if="hasPendingRequest" class="text-gray-400">
      У вас уже есть активная заявка на рассмотрении.
    </div>

    <!-- Форма для отправки заявки -->
    <form v-else @submit.prevent="submitForm" class="w-full max-w-md bg-gray-800 shadow-lg rounded-lg overflow-hidden p-6">
      <!-- Если есть отклонённая заявка, показываем сообщение -->
      <div v-if="lastRejectedRequest" class="mb-4 text-gray-400">
        Ваша предыдущая заявка на должность "{{ lastRejectedRequest.admin_position }}" была отклонена.
        <br />
        Комментарий администратора: {{ lastRejectedRequest.comment }}
      </div>

      <!-- Поле для ввода должности -->
      <div class="mb-4">
        <label for="admin_position" class="block text-sm font-medium text-gray-300 mb-2">
          Желаемая должность
        </label>
        <input
          type="text"
          id="admin_position"
          v-model="formData.admin_position"
          placeholder="Введите должность (например, Модератор)"
          class="w-full px-4 py-2 border border-gray-700 rounded-md bg-gray-700 text-gray-300 focus:outline-none focus:border-blue-500"
          required
        />
      </div>

      <!-- Кнопка отправки -->
      <button
        type="submit"
        :disabled="isSubmitting"
        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-md transition duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ isSubmitting ? 'Отправка...' : 'Отправить заявку' }}
      </button>

      <!-- Сообщение об ошибке -->
      <div v-if="errorMessage" class="mt-4 text-red-500 text-sm">
        {{ errorMessage }}
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useUserStore } from '@/stores/userStore.ts';
import { useConfigStore } from '@/stores/configStore.ts';
import axios from 'axios';

// Определяем типы
interface CheckPendingResponse {
  has_pending_request: boolean;
  last_rejected_request: {
    admin_position: string;
    comment: string;
  } | null;
}

const userStore = useUserStore();
const configStore = useConfigStore(); // Получаем доступ к хранилищу конфигурации
const isLoading = ref(false);
const isSubmitting = ref(false);
const hasPendingRequest = ref(false);
const lastRejectedRequest = ref<{ admin_position: string; comment: string } | null>(null);
const errorMessage = ref('');
const formData = ref<{ admin_position: string }>({ admin_position: '' });
const is_admin = ref(false);

// Проверка наличия активной или отклонённой заявки при загрузке компонента
async function checkPendingRejectedRequest() {
  try {
    isLoading.value = true;

    // Проверяем, загружены ли данные пользователя
    if (!userStore.userData?.id) {
      await userStore.loadUserData();
    }

    if (!userStore.userData?.id) {
      errorMessage.value = 'Данные пользователя не загружены. Пожалуйста, авторизуйтесь.';
      return;
    }

    const response = await axios.get<CheckPendingResponse>(
      `${configStore.backendBaseUrl}/api/v1/user/admin-request/check-pending-rejected-accepted/${userStore.userData.id}`
    );

    hasPendingRequest.value = response.data.has_pending_request;
    lastRejectedRequest.value = response.data.last_rejected_request;
    is_admin.value = response.data.is_admin;
  } catch (error) {
    console.error('Ошибка при проверке активной заявки:', error);
    errorMessage.value = 'Не удалось проверить наличие активной заявки.';
  } finally {
    isLoading.value = false;
  }
}

// Отправка формы
async function submitForm() {
  if (!formData.value.admin_position || !formData.value.admin_position.trim()) {
    errorMessage.value = 'Пожалуйста, укажите желаемую должность.';
    return;
  }

  try {
    isSubmitting.value = true;

    // Проверяем, загружены ли данные пользователя
    if (!userStore.userData?.id) {
      await userStore.loadUserData();
    }

    if (!userStore.userData?.id) {
      errorMessage.value = 'Данные пользователя не загружены. Пожалуйста, авторизуйтесь.';
      return;
    }

    const response = await axios.post(
      `${configStore.backendBaseUrl}/api/v1/user/admin-request/`,
      {
        user_id: userStore.userData.id,
        admin_position: formData.value.admin_position,
      }
    );

    if (response.status === 201) {
      formData.value.admin_position = ''; // Очищаем поле
      hasPendingRequest.value = true; // Обновляем состояние
      errorMessage.value = '';
    }
  } catch (error) {
    console.error('Ошибка при отправке заявки:', error);
    errorMessage.value = 'Произошла ошибка. Пожалуйста, попробуйте позже.';
  } finally {
    isSubmitting.value = false;
  }
}

// Инициализация
checkPendingRejectedRequest();
</script>