<template>
  <div class="min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-200">
    <div class="container mx-auto px-4 py-8">
      <!-- Блок ошибок -->
      <div
        v-if="errorMessage"
        class="mb-6 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded-r-lg p-4 shadow-md animate-fade-in"
      >
        <div class="flex items-start">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-500 dark:text-red-300" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
              Произошла ошибка
            </h3>
            <div class="mt-1 text-sm text-red-700 dark:text-red-300">
              <p>{{ errorMessage }}</p>
              <!-- Детали ошибки -->
              <div
                v-if="errorDetails && Object.keys(errorDetails).length"
                class="mt-2 pt-2 border-t border-red-200 dark:border-red-700/50"
              >
                <ul class="list-disc pl-5 space-y-1">
                  <li
                    v-for="(errors, field) in errorDetails"
                    :key="field"
                    class="text-xs"
                  >
                    <span class="font-semibold capitalize">{{ field.replace(/_/g, ' ') }}:</span>
                    <span class="ml-1 text-red-600 dark:text-red-400">
                      {{ Array.isArray(errors) ? errors.join(', ') : errors }}
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Заголовок -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          Редактирование комиссии
        </h1>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          ID: {{ commission_id || '—' }}
        </p>
      </div>

      <!-- Форма -->
      <div v-if="isCommissionFound" class="max-w-3xl mx-auto bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden">
        <!-- Карточка с информацией -->
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg">
              <p class="text-xs font-medium text-gray-500 dark:text-gray-400">Дата создания</p>
              <p class="mt-1 text-sm font-medium text-gray-900 dark:text-white">
                {{ formatDateTime(created_at) }}
              </p>
            </div>
            <div class="bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg">
              <p class="text-xs font-medium text-gray-500 dark:text-gray-400">Последнее изменение</p>
              <p class="mt-1 text-sm font-medium text-gray-900 dark:text-white">
                {{ formatDateTime(updated_at) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Поля формы -->
        <div class="p-6 space-y-6">
          <div>
            <label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Название комиссии
            </label>
            <input
              id="name"
              v-model="name"
              type="text"
              class="block w-full px-4 py-2.5 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-500 dark:focus:border-blue-500 transition"
              placeholder="Введите название"
              required
            >
          </div>

          <div>
            <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Описание
            </label>
            <textarea
              id="description"
              v-model="description"
              rows="4"
              class="block w-full px-4 py-2.5 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-500 dark:focus:border-blue-500 transition"
              placeholder="Добавьте описание комиссии"
            ></textarea>
          </div>
        </div>

        <!-- Футер формы -->
        <div class="bg-gray-50 dark:bg-gray-700/20 px-6 py-4 flex justify-end">
          <button
            type="button"
            @click="router.push('/admin_panel')"
            class="mr-3 px-4 py-2.5 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition"
          >
            Отмена
          </button>
          <button
            type="submit"
            @click.prevent="updateCommission"
            :disabled="isLoading"
            class="px-4 py-2.5 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition disabled:opacity-70 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="inline-flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Сохранение...
            </span>
            <span v-else>
              Сохранить изменения
            </span>
          </button>
        </div>
      </div>

      <!-- Если комиссия не найдена -->
      <div v-else class="max-w-md mx-auto text-center bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden p-8">
        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 dark:bg-red-900/30">
          <svg class="h-6 w-6 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </div>
        <h3 class="mt-3 text-lg font-medium text-gray-900 dark:text-white">
          Комиссия не найдена
        </h3>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
          Комиссия с ID {{ commissionId }} не существует или была удалена.
        </p>
        <div class="mt-6">
          <button
            @click="router.push('/admin_panel')"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-offset-gray-800 transition"
          >
            Вернуться к списку комиссий
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { useConfigStore } from '@/stores/configStore'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const configStore = useConfigStore()

const commissionId = route.params.id

// Состояния формы
const name = ref('')
const description = ref('')
const created_at = ref('')
const updated_at = ref('')
const commission_id = ref<string | null>(null)
const isLoading = ref(false)
const isCommissionFound = ref(true)

// Ошибки
const errorMessage = ref('')
const errorDetails = ref<Record<string, any>>({})

// Форматирование даты
const formatDateTime = (dateString: string): string => {
  if (!dateString) return '—'
  try {
    const date = new Date(dateString)
    return isNaN(date.getTime())
      ? 'Некорректная дата'
      : date.toLocaleString('ru-RU', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
  } catch {
    return 'Некорректная дата'
  }
}

// Загрузка данных
const loadCommissionData = async () => {
  try {
    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/service/commission_detail/${commissionId}/`)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(
        errorData.message ||
        errorData.detail ||
        'Не удалось загрузить данные комиссии'
      )
    }

    const data = await response.json()
    name.value = data.name
    description.value = data.description
    created_at.value = data.created_at
    updated_at.value = data.updated_at
    commission_id.value = data.id
  } catch (error) {
    console.error('Ошибка загрузки:', error)
    isCommissionFound.value = false
    errorMessage.value = error instanceof Error
      ? error.message
      : 'Произошла неизвестная ошибка'
  }
}

// Обновление комиссии
const updateCommission = async () => {
  errorMessage.value = '';
  errorDetails.value = {};
  isLoading.value = true;

  try {
    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/admin/update_commission/${commissionId}/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userStore.userData?.id,
        name: name.value.trim(),
        description: description.value.trim(),
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      errorMessage.value = data.message || 'Ошибка при обновлении комиссии';

      // Обрабатываем детали ошибки
      if (data.details) {
        errorDetails.value = data.details;
      } else if (data.errors) {
        // Для совместимости со старым форматом
        errorDetails.value = data.errors;
      }

      return;
    }

    // Успешное обновление
    updated_at.value = data.data?.updated_at || data.updated_at;
    await router.push({
      path: '/admin_panel',
      query: { success: 'Комиссия успешно обновлена' }
    });
  } catch (error) {
    errorMessage.value = 'Ошибка сети. Попробуйте позже.';
    console.error('Ошибка:', error);
  } finally {
    isLoading.value = false;
  }
};

// Загрузка при монтировании
onMounted(loadCommissionData)
</script>