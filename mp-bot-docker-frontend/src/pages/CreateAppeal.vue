<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-4">
    <!-- Приветственное сообщение -->
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Написать обращение
    </h1>

    <!-- Проверка наличия комиссий -->
    <div v-if="isEmptyCommissions" class="w-full max-w-2xl bg-gray-800 shadow-lg rounded-lg overflow-hidden p-6 text-center">
      <p class="text-gray-400 text-lg">
        К сожалению, сейчас нет доступных комиссий для обращения.
      </p>
    </div>

    <!-- Блок для отображения ошибок -->
    <div v-if="Object.keys(errors).length > 0" class="w-full max-w-2xl bg-red-800 text-white rounded-lg p-4 mb-4">
      <h2 class="text-lg font-bold mb-2">Ошибки валидации:</h2>
      <pre class="text-sm whitespace-pre-wrap break-words">{{ JSON.stringify(errors, null, 2) }}</pre>
    </div>

    <!-- Форма для создания обращения -->
    <form v-if="!isEmptyCommissions" @submit.prevent="submitAppeal" class="w-full max-w-2xl bg-gray-800 shadow-lg rounded-lg overflow-hidden p-6">
      <!-- Поле для текста обращения -->
      <div class="mb-4">
        <label for="appeal_text" class="block text-sm font-medium text-gray-300">Текст обращения</label>
        <textarea
          id="appeal_text"
          v-model="appealText"
          rows="5"
          class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Введите текст обращения (минимум 100 символов)"
          required
        ></textarea>
      </div>

      <!-- Выбор комиссии -->
      <div class="mb-4">
        <label for="commission_select" class="block text-sm font-medium text-gray-300">Выберите комиссию</label>
        <select
          id="commission_select"
          v-model="selectedCommission"
          class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="" disabled selected>Выберите комиссию</option>
          <option v-for="commission in commissions" :key="commission.id" :value="commission.id">
            {{ commission.name }}
          </option>
        </select>
      </div>

      <!-- Поле для контактной информации -->
      <div class="mb-4">
        <label for="contact_info" class="block text-sm font-medium text-gray-300">
          Контактная информация (опционально)
        </label>
        <input
          id="contact_info"
          v-model="contactInfo"
          type="text"
          class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Введите email или номер телефона РФ"
        />
      </div>

      <!-- Поле для загрузки файла -->
      <div class="mb-4">
        <label for="file_upload" class="block text-sm font-medium text-gray-300">Прикрепить файл (опционально)</label>
        <input
          id="file_upload"
          type="file"
          @change="handleFileUpload"
          class="mt-1 block w-full text-white text-sm cursor-pointer bg-gray-700 border border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <!-- Кнопка отправки -->
      <button
        type="submit"
        :disabled="isLoading"
        class="w-full px-4 py-2 bg-blue-500 text-white font-semibold rounded-md hover:bg-blue-600 transition-colors duration-200 disabled:bg-gray-500"
      >
        {{ isLoading ? 'Отправка...' : 'Отправить обращение' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from "@/stores/userStore.ts";
import { useConfigStore } from "@/stores/configStore.ts"; // Импортируем хранилище конфигурации

// Инициализируем хранилища
const userStore = useUserStore();
const configStore = useConfigStore(); // Получаем доступ к хранилищу конфигурации
const router = useRouter();

// Состояния для полей формы
const appealText = ref('');
const contactInfo = ref('');
const file = ref<File | null>(null);
const selectedCommission = ref<string | null>(null);
const commissions = ref<{ id: string; name: string; description: string }[]>([]);
const errors = ref<any>({});
const isLoading = ref(false);

// Флаг "нет комиссий"
const isEmptyCommissions = computed(() => commissions.value.length === 0);

onMounted(async () => {
  try {
    const response = await fetch(`${configStore.backendBaseUrl}/commissions/`); // Используем backendBaseUrl
    if (response.ok) {
      commissions.value = await response.json();
    } else {
      console.error('Ошибка при загрузке комиссий');
    }
  } catch (error) {
    console.error('Ошибка сети:', error);
  }
});

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    file.value = target.files[0];
  }
};

const submitAppeal = async () => {
  errors.value = {}; // Очищаем предыдущие ошибки
  isLoading.value = true;

  try {
    const formData = new FormData();
    formData.append('appeal_text', appealText.value);
    formData.append('user_id', userStore.userData.user_id);
    formData.append('commission_id', selectedCommission.value || '');
    if (contactInfo.value) formData.append('contact_info', contactInfo.value);
    if (file.value) formData.append('file', file.value);

    const response = await fetch(`${configStore.backendBaseUrl}/appeal_create/`, { // Используем backendBaseUrl
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      alert('Обращение успешно отправлено!');
      await router.push('/my_appeals');
    } else {
      const errorData = await response.json();
      errors.value = errorData.errors || {};
    }
  } catch (error) {
    console.error('Ошибка:', error.message);
    alert(`Ошибка при отправке обращения: ${error.message}`);
  } finally {
    isLoading.value = false;
  }
};
</script>