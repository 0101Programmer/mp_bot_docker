<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-4">
    <!-- Приветственное сообщение -->
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Список комиссий
    </h1>

    <!-- Проверка наличия комиссий -->
    <div v-if="isEmptyCommissions" class="w-full max-w-2xl bg-gray-800 shadow-lg rounded-lg overflow-hidden p-6 text-center">
      <p class="text-gray-400 text-lg">
        К сожалению, сейчас нет доступных комиссий.
      </p>
    </div>

    <!-- Выбор комиссии -->
    <div v-else class="w-full max-w-2xl bg-gray-800 shadow-lg rounded-lg overflow-hidden p-6">
      <label for="commission_select" class="block text-sm font-medium text-gray-300 mb-2">
        Выберите комиссию
      </label>
      <select
        id="commission_select"
        v-model="selectedCommissionId"
        @change="fetchSelectedCommission"
        class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="" disabled selected>Выберите комиссию</option>
        <option v-for="commission in commissions" :key="commission.id" :value="commission.id">
          {{ commission.name }}
        </option>
      </select>

      <!-- Описание выбранной комиссии -->
      <div v-if="selectedCommission" class="mt-6">
        <h2 class="text-xl font-bold text-blue-400 mb-2">{{ selectedCommission.name }}</h2>
        <p class="text-gray-300 whitespace-pre-wrap">{{ selectedCommission.description || 'Описание отсутствует.' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useConfigStore } from '@/stores/configStore.ts'; // Импортируем хранилище конфигурации

// Инициализируем хранилище конфигурации
const configStore = useConfigStore();

// Состояния для данных
const commissions = ref<{ id: string; name: string; description: string }[]>([]);
const selectedCommissionId = ref<string | null>(null);
const selectedCommission = ref<{ id: string; name: string; description: string } | null>(null);

// Флаги
const isEmptyCommissions = ref(false);

// Загрузка списка комиссий при монтировании компонента
onMounted(async () => {
  try {
    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/service/commissions/`); // Используем backendBaseUrl
    if (response.ok) {
      const data = await response.json();
      commissions.value = data;
      isEmptyCommissions.value = data.length === 0;
    } else {
      console.error('Ошибка при загрузке комиссий');
    }
  } catch (error) {
    console.error('Ошибка сети:', error);
  }
});

// Функция для выбора комиссии
const fetchSelectedCommission = () => {
  if (selectedCommissionId.value) {
    const commission = commissions.value.find((c) => c.id === selectedCommissionId.value);
    if (commission) {
      selectedCommission.value = commission;
    }
  } else {
    selectedCommission.value = null;
  }
};
</script>