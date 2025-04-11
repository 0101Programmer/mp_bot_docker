<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-4">
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Заявки на права администратора
    </h1>

    <!-- Блок для отображения ошибок -->
    <div v-if="errorMessage" class="w-full max-w-4xl mb-4 p-3 bg-red-500 text-white rounded-md">
      {{ errorMessage }}
    </div>

    <div v-if="isLoading" class="text-gray-400">
      Загрузка данных...
    </div>

    <div v-else-if="requests.length > 0" class="w-full max-w-4xl bg-gray-800 shadow-lg rounded-lg overflow-x-auto">
      <table class="w-full text-sm text-left text-gray-400">
        <thead class="text-xs uppercase bg-gray-700 text-gray-300">
          <tr>
            <th scope="col" class="px-4 py-3">ID</th>
            <th scope="col" class="px-4 py-3">Пользователь</th>
            <th scope="col" class="px-4 py-3">Должность</th>
            <th scope="col" class="px-4 py-3 whitespace-nowrap">Дата создания</th>
            <th scope="col" class="px-4 py-3 whitespace-nowrap">Последнее изменение</th>
            <th scope="col" class="px-4 py-3">Статус</th>
            <th scope="col" class="px-4 py-3">Действия</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="request in requests" :key="request.id" class="border-b border-gray-700 hover:bg-gray-700">
            <td class="px-4 py-4 font-mono">{{ request.id }}</td>
            <td class="px-4 py-4 font-medium text-white">{{ request.user.username }}</td>
            <td class="px-4 py-4">{{ request.admin_position }}</td>

            <td class="px-4 py-4 whitespace-nowrap">
              <div class="flex flex-col">
                <span>{{ formatDate(request.created_at) }}</span>
                <span class="text-xs text-gray-400">{{ formatTime(request.created_at) }}</span>
              </div>
            </td>

            <td class="px-4 py-4 whitespace-nowrap">
              <div class="flex flex-col">
                <span>{{ formatDate(request.updated_at) }}</span>
                <span class="text-xs text-gray-400">{{ formatTime(request.updated_at) }}</span>
              </div>
            </td>

            <td class="px-4 py-4">
              <div class="flex flex-col space-y-2">
                <span :class="statusColor(request.status)" class="font-semibold">
                  {{ getStatusDisplay(request.status) }}
                </span>

                <select
                  v-if="request.status === 'pending'"
                  v-model="request.status"
                  @change="onStatusChange(request)"
                  class="block w-full px-3 py-1 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="approved">Одобрено</option>
                  <option value="rejected">Отклонено</option>
                </select>

                <div v-if="request.isRejectionMode" class="mt-2">
                  <textarea
                    v-model="request.comment"
                    placeholder="Причина отклонения..."
                    class="block w-full px-3 py-2 text-sm bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows="2"
                  ></textarea>
                  <!-- Отображение ошибки под текстовым полем -->
                  <div v-if="request.showCommentError" class="text-red-400 text-xs mt-1">
                    Пожалуйста, укажите причину отклонения
                  </div>
                  <button
                    @click="confirmRejection(request)"
                    class="mt-2 px-3 py-1 text-sm bg-red-500 text-white font-medium rounded-md hover:bg-red-600 transition-colors duration-200"
                  >
                    Подтвердить
                  </button>
                </div>
              </div>
            </td>

            <td class="px-4 py-4">
              <button
                @click="confirmDelete(request.id)"
                class="px-3 py-1 text-sm bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors duration-200"
                title="Удалить заявку"
              >
                Удалить
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="text-gray-400 py-8">
      Нет заявок для отображения
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore';
import { useConfigStore } from '@/stores/configStore';

interface AdminRequest {
  id: number;
  user: {
    id: number;
    username: string;
  };
  admin_position: string;
  status: 'pending' | 'approved' | 'rejected';
  comment?: string;
  created_at: string;
  updated_at: string;
  isRejectionMode?: boolean;
}

const router = useRouter();
const userStore = useUserStore();
const configStore = useConfigStore();

const requests = ref<AdminRequest[]>([]);
const isLoading = ref(true);
const errorMessage = ref<string | null>(null);

// Функции форматирования
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

const getStatusDisplay = (status: string): string => {
  const statusMap = {
    'pending': 'На рассмотрении',
    'approved': 'Одобрено',
    'rejected': 'Отклонено'
  };
  return statusMap[status as keyof typeof statusMap] || status;
};

const statusColor = (status: string): string => {
  const colors = {
    'pending': 'text-yellow-400',
    'approved': 'text-green-400',
    'rejected': 'text-red-400'
  };
  return colors[status as keyof typeof colors] || 'text-white';
};

// Загрузка данных
const fetchAdminRequests = async () => {
  try {
    isLoading.value = true;
    errorMessage.value = null;

    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/admin/admin_requests/`);

    if (!response.ok) {
      throw new Error('Не удалось загрузить заявки');
    }

    requests.value = (await response.json()).map((req: AdminRequest) => ({
      ...req,
      isRejectionMode: false,
      showCommentError: false
    }));

  } catch (error) {
    console.error('Ошибка загрузки:', error);
    errorMessage.value = error instanceof Error ? error.message : 'Неизвестная ошибка';
  } finally {
    isLoading.value = false;
  }
};

// Обработка изменения статуса
const onStatusChange = (request: AdminRequest) => {
  if (request.status === 'rejected') {
    request.isRejectionMode = true;
  } else {
    updateRequestStatus(request.id, request.status);
  }
};

const confirmRejection = async (request: AdminRequest) => {
  if (!request.comment?.trim()) {
    request.showCommentError = true;
    errorMessage.value = 'Пожалуйста, укажите причину отклонения';
    return;
  }

  request.showCommentError = false;
  errorMessage.value = null;
  await updateRequestStatus(request.id, request.status);
  request.isRejectionMode = false;
};

const updateRequestStatus = async (id: number, status: string) => {
  try {
    const response = await fetch(
      `${configStore.backendBaseUrl}/api/v1/admin/update_admin_request_status/${id}/`,
      {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userStore.userData?.id,
          status,
          comment: requests.value.find(r => r.id === id)?.comment || null
        })
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Ошибка обновления статуса');
    }

    const index = requests.value.findIndex(r => r.id === id);
    if (index !== -1) {
      requests.value[index].status = status;
    }

  } catch (error) {
    console.error('Ошибка обновления:', error);
    errorMessage.value = error instanceof Error ? error.message : 'Ошибка обновления статуса';
  }
};

// Удаление заявки
const deleteRequest = async (id: number) => {
  try {
    const response = await fetch(
      `${configStore.backendBaseUrl}/api/v1/admin/delete_admin_request/${id}/`,
      {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userStore.userData?.id })
      }
    );

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Ошибка удаления');
    }

    requests.value = requests.value.filter(r => r.id !== id);

  } catch (error) {
    console.error('Ошибка удаления:', error);
    errorMessage.value = error instanceof Error ? error.message : 'Ошибка удаления заявки';
  }
};

const confirmDelete = (id: number) => {
  if (confirm('Вы уверены, что хотите удалить эту заявку? Это действие нельзя отменить.')) {
    deleteRequest(id);
  }
};

onMounted(() => {
  fetchAdminRequests();
});
</script>