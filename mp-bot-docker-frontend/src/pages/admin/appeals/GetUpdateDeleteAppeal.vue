<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-4">

    <!-- Модальное окно для полного текста -->
    <div v-if="selectedAppeal" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div class="bg-gray-800 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex justify-between items-start mb-4">
            <h3 class="text-xl font-bold text-blue-400">Полный текст обращения #{{ selectedAppeal.id }}</h3>
            <button @click="selectedAppeal = null" class="text-gray-400 hover:text-white">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="whitespace-pre-line break-words overflow-wrap-break-word bg-gray-700 p-4 rounded-md mb-4">
            {{ selectedAppeal.appeal_text }}
          </div>
          <div class="text-sm text-gray-400">
            <p>Дата создания: {{ formatDateTime(selectedAppeal.created_at) }}</p>
            <p>Последнее обновление: {{ formatDateTime(selectedAppeal.updated_at) }}</p>
            <p v-if="selectedAppeal.contact_info">Контакты: {{ selectedAppeal.contact_info }}</p>
            <p v-if="selectedAppeal.commission">Комиссия: {{ selectedAppeal.commission_name }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Остальной контент страницы -->
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Список обращений
    </h1>

    <!-- Поле для фильтрации обращений -->
    <div class="w-full max-w-6xl mb-6 px-4">
      <label for="filter_id" class="block text-sm font-medium text-gray-300">Фильтр по ID обращения</label>
      <input
        id="filter_id"
        v-model="filterId"
        type="number"
        class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Введите ID обращения"
      />
    </div>

    <!-- Если данные загружаются -->
    <div v-if="isLoading" class="text-gray-400">
      Загрузка данных...
    </div>

    <!-- Если данные загружены -->
    <div v-else-if="filteredAppeals.length > 0" class="w-full max-w-6xl bg-gray-800 shadow-lg rounded-lg overflow-x-auto">
      <div class="min-w-[1100px]"> <!-- Увеличили минимальную ширину -->
        <table class="w-full text-sm text-left text-gray-400">
          <!-- Заголовок таблицы -->
          <thead class="text-xs uppercase bg-gray-700 text-gray-300">
            <tr>
              <th scope="col" class="px-4 py-3 sticky left-0 bg-gray-700 z-10">ID</th>
              <th scope="col" class="px-4 py-3 min-w-[120px]">Дата создания</th>
              <th scope="col" class="px-4 py-3 min-w-[120px]">Обновлено</th>
              <th scope="col" class="px-4 py-3 min-w-[150px]">Комиссия</th>
              <th scope="col" class="px-4 py-3 min-w-[200px]">Текст заявки</th>
              <th scope="col" class="px-4 py-3 min-w-[150px]">Контакты</th>
              <th scope="col" class="px-4 py-3 min-w-[100px]">Файл</th>
              <th scope="col" class="px-4 py-3 min-w-[120px]">Статус</th>
              <th scope="col" class="px-4 py-3 min-w-[100px] sticky right-0 bg-gray-700 z-10">Действия</th>
            </tr>
          </thead>

          <!-- Тело таблицы -->
          <tbody>
            <tr v-for="appeal in filteredAppeals" :key="appeal.id" class="border-b border-gray-700 hover:bg-gray-700">
              <td class="px-4 py-4 font-mono sticky left-0 bg-gray-800 z-10">{{ appeal.id }}</td>
              <td class="px-4 py-4 whitespace-nowrap">
                <div class="flex flex-col">
                  <span>{{ formatDate(appeal.created_at) }}</span>
                  <span class="text-xs text-gray-400">{{ formatTime(appeal.created_at) }}</span>
                </div>
              </td>
              <td class="px-4 py-4 whitespace-nowrap">
                <div class="flex flex-col">
                  <span>{{ formatDate(appeal.updated_at) }}</span>
                  <span class="text-xs text-gray-400">{{ formatTime(appeal.updated_at) }}</span>
                </div>
              </td>
              <td class="px-4 py-4 max-w-[150px] break-words">
                {{ appeal.commission_name || 'Не указана' }}
              </td>
              <td class="px-4 py-4 max-w-[200px]">
                <button
                  @click="selectedAppeal = appeal"
                  class="text-left w-full text-blue-400 hover:text-blue-300 hover:underline line-clamp-3"
                >
                  {{ appeal.appeal_text }}
                </button>
              </td>
              <td class="px-4 py-4 max-w-[150px] break-words">
                {{ appeal.contact_info || '-' }}
              </td>
              <td class="px-4 py-4 whitespace-nowrap">
                <a
                  v-if="appeal.file_path"
                  :href="`${configStore.backendBaseUrl}/api/v1/service/download/${appeal.id}`"
                  class="text-blue-400 hover:text-blue-300 transition-colors duration-200"
                  target="_blank"
                >
                  Скачать
                </a>
                <span v-else>Нет файла</span>
              </td>
              <td class="px-4 py-4">
                <div class="flex flex-col space-y-2 min-w-[110px]">
                  <span class="font-semibold">{{ getStatusDisplay(appeal.status) }}</span>
                  <select
                    v-if="appeal.status === 'new'"
                    v-model="appeal.status"
                    @change="updateStatus(appeal.id, appeal.status)"
                    class="block w-full px-2 py-1 text-sm bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="processed">Обработано</option>
                    <option value="rejected">Отклонено</option>
                  </select>
                </div>
              </td>
              <td class="px-4 py-4 sticky right-0 bg-gray-800 z-10">
                <button
                  @click="confirmDelete(appeal.id)"
                  class="px-3 py-1 text-sm bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors duration-200"
                >
                  Удалить
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Если данных нет -->
    <div v-else class="text-gray-400 py-8">
      Нет данных для отображения.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore.ts';
import { useConfigStore } from '@/stores/configStore';

const router = useRouter();
const userStore = useUserStore();
const configStore = useConfigStore();

const appeals = ref<any[]>([]);
const isLoading = ref(true);
const filterId = ref<number | null>(null);
const selectedAppeal = ref<any>(null);

// Функции форматирования даты и времени
const formatDate = (dateString: string): string => {
  if (!dateString) return '—';
  try {
    const date = new Date(dateString);
    return isNaN(date.getTime())
      ? 'Некорректная дата'
      : date.toLocaleDateString('ru-RU');
  } catch {
    return 'Некорректная дата';
  }
};

const formatTime = (dateString: string): string => {
  if (!dateString) return '—';
  try {
    const date = new Date(dateString);
    return isNaN(date.getTime())
      ? 'Некорректное время'
      : date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  } catch {
    return 'Некорректное время';
  }
};

const formatDateTime = (dateString: string): string => {
  if (!dateString) return '—';
  try {
    const date = new Date(dateString);
    return isNaN(date.getTime())
      ? 'Некорректная дата'
      : date.toLocaleString('ru-RU', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
  } catch {
    return 'Некорректная дата';
  }
};

onMounted(async () => {
  try {
    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/admin/appeals/`);
    if (response.ok) {
      appeals.value = await response.json();
      // Добавляем проверку на наличие комиссии
      appeals.value.forEach(appeal => {
        if (!appeal.commission) {
          appeal.commission = { name: 'Не указана' };
        }
      });
    } else {
      console.error('Ошибка при загрузке данных обращений');
    }
  } catch (error) {
    console.error('Ошибка сети:', error);
  } finally {
    isLoading.value = false;
  }
});

const filteredAppeals = computed(() => {
  if (!filterId.value) return appeals.value;
  return appeals.value.filter((appeal) => appeal.id === filterId.value);
});

const updateStatus = async (id: number, status: string) => {
  try {
    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/admin/update_appeal_status/${id}/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userStore.userData?.id,
        status,
      }),
    });

    if (response.ok) {
      // Обновляем дату изменения в локальном состоянии
      const index = appeals.value.findIndex(a => a.id === id);
      if (index !== -1) {
        appeals.value[index].updated_at = new Date().toISOString();
      }
      alert('Статус успешно обновлен.');
    } else {
      const errorData = await response.json();
      alert(errorData.message || 'Произошла ошибка при обновлении статуса.');
    }
  } catch (error) {
    console.error('Ошибка:', error.message);
    alert(`Ошибка при обновлении статуса: ${error.message}`);
  }
};

const confirmDelete = (id: number) => {
  if (confirm('Вы уверены, что хотите удалить это обращение?')) {
    deleteAppeal(id);
  }
};

const deleteAppeal = async (id: number) => {
  try {
    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/admin/delete_appeal/${id}/`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userStore.userData?.id,
      }),
    });

    if (response.ok) {
      alert('Обращение успешно удалено.');
      appeals.value = appeals.value.filter((appeal) => appeal.id !== id);
    } else {
      const errorData = await response.json();
      alert(errorData.message || 'Произошла ошибка при удалении обращения.');
    }
  } catch (error) {
    console.error('Ошибка:', error.message);
    alert(`Ошибка при удалении обращения: ${error.message}`);
  }
};

const getStatusDisplay = (status: string) => {
  const statusMap: Record<string, string> = {
    'new': 'Новое',
    'processed': 'Обработано',
    'rejected': 'Отклонено',
  };
  return statusMap[status] || status;
};
</script>