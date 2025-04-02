<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-4">
    <!-- Приветственное сообщение -->
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Заявки на права администратора
    </h1>

    <!-- Если данные загружаются -->
    <div v-if="isLoading" class="text-gray-400">
      Загрузка данных...
    </div>

    <!-- Если данные загружены -->
    <div v-else-if="requests.length > 0" class="w-full max-w-4xl bg-gray-800 shadow-lg rounded-lg overflow-hidden">
      <table class="w-full text-sm text-left text-gray-400">
        <!-- Заголовок таблицы -->
        <thead class="text-xs uppercase bg-gray-700 text-gray-300">
          <tr>
            <th scope="col" class="px-6 py-3">ID</th>
            <th scope="col" class="px-6 py-3">Пользователь</th>
            <th scope="col" class="px-6 py-3">Должность</th>
            <th scope="col" class="px-6 py-3">Дата подачи</th>
            <th scope="col" class="px-6 py-3">Статус</th>
            <th scope="col" class="px-6 py-3">Действия</th>
          </tr>
        </thead>

        <!-- Тело таблицы -->
        <tbody>
          <tr v-for="request in requests" :key="request.id" class="border-b border-gray-700 hover:bg-gray-700">
            <td class="px-6 py-4">{{ request.id }}</td>
            <td class="px-6 py-4">{{ request.user.username }}</td>
            <td class="px-6 py-4">{{ request.admin_position }}</td>
            <td class="px-6 py-4">{{ formatDate(request.timestamp) }}</td>
            <td class="px-6 py-4">
              <div class="space-y-2">
                <!-- Отображение текущего статуса -->
                <span class="font-semibold">{{ request.status }}</span>
                <!-- Выпадающий список для изменения статуса -->
                <select
                  v-if="request.status === 'pending'"
                  v-model="request.status"
                  @change="onStatusChange(request)"
                  class="block w-full px-3 py-1 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="approved">Одобрено</option>
                  <option value="rejected">Отклонено</option>
                </select>
                <!-- Поле для комментария при отклонении -->
                <div v-if="request.isRejectionMode">
                  <textarea
                    v-model="request.comment"
                    placeholder="Введите комментарий..."
                    class="block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
                  ></textarea>
                  <button
                    @click="confirmRejection(request)"
                    class="px-4 py-2 bg-red-500 text-white font-semibold rounded-md hover:bg-red-600 transition-colors duration-200"
                  >
                    Подтвердить отклонение
                  </button>
                </div>
              </div>
            </td>
            <td class="px-6 py-4">
              <button
                @click="confirmDelete(request.id)"
                class="text-red-500 hover:text-red-400 transition-colors duration-200"
              >
                Удалить
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Если данных нет -->
    <div v-else class="text-gray-400">
      Нет данных для отображения.
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../../../stores/userStore';

// Инициализируем роутер и хранилище пользователя
const router = useRouter();
const userStore = useUserStore();

// Состояния для данных заявок
const requests = ref<any[]>([]);
const isLoading = ref(true);

// Загрузка данных заявок
onMounted(async () => {
  try {
    const response = await fetch('http://localhost:8000/telegram_bot/api/v1/admin/admin_requests/');
    if (response.ok) {
      requests.value = await response.json();
      // Инициализируем режим отклонения
      requests.value.forEach((req) => {
        req.isRejectionMode = false; // Флаг для режима отклонения
      });
    } else {
      console.error('Ошибка при загрузке данных заявок');
    }
  } catch (error) {
    console.error('Ошибка сети:', error);
  } finally {
    isLoading.value = false;
  }
});

// Форматирование даты
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString(); // Локальное форматирование даты и времени
};

// Обработка изменения статуса
const onStatusChange = (request: any) => {
  if (request.status === 'rejected') {
    request.isRejectionMode = true; // Включаем режим отклонения
  } else {
    updateStatus(request.id, request.status); // Обновляем статус напрямую
  }
};

// Подтверждение отклонения
const confirmRejection = async (request: any) => {
  if (!request.comment) {
    alert('Пожалуйста, укажите комментарий.');
    return;
  }

  await updateStatus(request.id, request.status);
  request.isRejectionMode = false; // Выходим из режима отклонения
};

// Обновление статуса заявки
const updateStatus = async (id: number, status: string) => {
  try {
    const requestData = requests.value.find((req) => req.id === id);
    if (!requestData) {
      alert('Заявка не найдена.');
      return;
    }

    const response = await fetch(`http://localhost:8000/telegram_bot/api/v1/admin/update_admin_request_status/${id}/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userStore.userData?.user_id, // Передаем user_id из хранилища
        status,
        comment: requestData.comment || null, // Передаем комментарий, если он есть
      }),
    });

    if (response.ok) {
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

// Подтверждение удаления заявки
const confirmDelete = (id: number) => {
  if (confirm('Вы уверены, что хотите удалить эту заявку?')) {
    deleteRequest(id);
  }
};

// Удаление заявки
const deleteRequest = async (id: number) => {
  try {
    const response = await fetch(`http://localhost:8000/telegram_bot/api/v1/admin/delete_admin_request/${id}/`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: userStore.userData?.user_id, // Передаем user_id из хранилища
      }),
    });

    if (response.ok) {
      alert('Заявка успешно удалена.');
      requests.value = requests.value.filter((req) => req.id !== id); // Удаляем из списка
    } else {
      const errorData = await response.json();
      alert(errorData.message || 'Произошла ошибка при удалении заявки.');
    }
  } catch (error) {
    console.error('Ошибка:', error.message);
    alert(`Ошибка при удалении заявки: ${error.message}`);
  }
};
</script>