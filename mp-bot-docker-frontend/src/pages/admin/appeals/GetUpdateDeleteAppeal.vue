<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-4">
    <!-- Приветственное сообщение -->
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Список обращений
    </h1>

    <!-- Поле для фильтрации обращений -->
    <div class="w-full max-w-4xl mb-6">
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
    <div v-else-if="filteredAppeals.length > 0" class="w-full max-w-4xl bg-gray-800 shadow-lg rounded-lg overflow-hidden">
      <table class="w-full text-sm text-left text-gray-400">
        <!-- Заголовок таблицы -->
        <thead class="text-xs uppercase bg-gray-700 text-gray-300">
          <tr>
            <th scope="col" class="px-6 py-3">ID</th>
            <th scope="col" class="px-6 py-3">Текст заявки</th>
            <th scope="col" class="px-6 py-3">Контактная информация</th>
            <th scope="col" class="px-6 py-3">Файл</th>
            <th scope="col" class="px-6 py-3">Статус</th>
            <th scope="col" class="px-6 py-3">Действия</th>
          </tr>
        </thead>

        <!-- Тело таблицы -->
        <tbody>
          <tr v-for="appeal in filteredAppeals" :key="appeal.id" class="border-b border-gray-700 hover:bg-gray-700">
            <td class="px-6 py-4">{{ appeal.id }}</td>
            <td class="px-6 py-4 max-w-[300px] break-words whitespace-normal">
              {{ appeal.appeal_text }}
            </td>
            <td class="px-6 py-4">{{ appeal.contact_info || '-' }}</td>
            <td class="px-6 py-4">
              <a
                v-if="appeal.file_path"
                :href="`http://localhost:8000/telegram_bot/api/v1/service/download/${appeal.id}`"
                class="text-blue-400 hover:text-blue-300 transition-colors duration-200"
                target="_blank"
              >
                Скачать файл
              </a>
              <span v-else>Нет файла</span>
            </td>
            <td class="px-6 py-4">
              <div class="space-y-2">
                <!-- Отображение текущего статуса -->
                <span class="font-semibold">{{ getStatusDisplay(appeal.status) }}</span>
                <!-- Выпадающий список для изменения статуса (только для новых обращений) -->
                <select
                  v-if="appeal.status === 'new'"
                  v-model="appeal.status"
                  @change="updateStatus(appeal.id, appeal.status)"
                  class="block w-full px-3 py-1 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="processed">Обработано</option>
                  <option value="rejected">Отклонено</option>
                </select>
              </div>
            </td>
            <td class="px-6 py-4">
              <button
                @click="confirmDelete(appeal.id)"
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
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore.ts';
import { useConfigStore } from '@/stores/configStore';

// Инициализируем роутер и хранилища
const router = useRouter();
const userStore = useUserStore();
const configStore = useConfigStore();

// Состояния для данных обращений
const appeals = ref<any[]>([]);
const isLoading = ref(true);
const filterId = ref<number | null>(null);

// Загрузка данных обращений
onMounted(async () => {
  try {
    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/admin/appeals/`);
    if (response.ok) {
      appeals.value = await response.json();
    } else {
      console.error('Ошибка при загрузке данных обращений');
    }
  } catch (error) {
    console.error('Ошибка сети:', error);
  } finally {
    isLoading.value = false;
  }
});

// Вычисляемые свойства для фильтрации обращений
const filteredAppeals = computed(() => {
  if (!filterId.value) return appeals.value; // Если фильтр пустой, показываем все обращения
  return appeals.value.filter((appeal) => appeal.id === filterId.value);
});

// Обновление статуса обращения
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

// Подтверждение удаления обращения
const confirmDelete = (id: number) => {
  if (confirm('Вы уверены, что хотите удалить это обращение?')) {
    deleteAppeal(id);
  }
};

// Удаление обращения
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
      appeals.value = appeals.value.filter((appeal) => appeal.id !== id); // Удаляем из списка
    } else {
      const errorData = await response.json();
      alert(errorData.message || 'Произошла ошибка при удалении обращения.');
    }
  } catch (error) {
    console.error('Ошибка:', error.message);
    alert(`Ошибка при удалении обращения: ${error.message}`);
  }
};
// Функция для отображения статуса на русском
const getStatusDisplay = (status: string) => {
  const statusMap: Record<string, string> = {
    'new': 'Новое',
    'processed': 'Обработано',
    'rejected': 'Отклонено',
  };
  return statusMap[status] || status;
};
</script>