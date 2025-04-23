<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useUserStore } from '@/stores/userStore.ts';
import { useRouter } from 'vue-router';
import { useConfigStore } from '@/stores/configStore.ts';

const userStore = useUserStore();
const configStore = useConfigStore();
const router = useRouter();

const isLoading = ref(true);
const appeals = ref([]);
const isModalOpen = ref(false);
const selectedAppealText = ref('');

const getStatusDisplay = (status: string) => {
  const statusMap = {
    'new': 'Новое',
    'processed': 'Обработано',
    'rejected': 'Отклонено'
  };
  return statusMap[status] || status;
};

const confirmDelete = (appealId: number) => {
  const isConfirmed = confirm(
    "Удаление обращения очистит всю его историю, а также отзовёт его, в случае, если оно не было обработано. Вы уверены?"
  );
  if (isConfirmed) {
    deleteAppeal(appealId);
  }
};

const deleteAppeal = async (appealId: number) => {
  try {
    const userId = userStore.userData?.id;
    if (!userId) {
      throw new Error('User ID не найден.');
    }

    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/user/appeal/${appealId}/delete/?user_id=${userId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Ошибка при удалении обращения.');
    }

    appeals.value = appeals.value.filter((appeal) => appeal.id !== appealId);
  } catch (error) {
    console.error('Ошибка:', error.message);
    alert(`Ошибка при удалении обращения: ${error.message}`);
  }
};

// Метод для копирования текста (обновленный)
const copyToClipboard = (text: string) => {
  try {
    // Создаем временный textarea элемент
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    document.body.appendChild(textarea);
    textarea.select();

    // Пытаемся использовать современный API
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(() => {
        showCopySuccess();
      }).catch(() => {
        // Если современный API не сработал, используем старый способ
        fallbackCopy(textarea);
      });
    } else {
      // Используем старый способ, если Clipboard API недоступен
      fallbackCopy(textarea);
    }

    // Удаляем временный элемент
    document.body.removeChild(textarea);
  } catch (error) {
    console.error('Ошибка при копировании текста:', error);
    alert('Не удалось скопировать текст. Попробуйте выделить текст вручную и скопировать его.');
  }
};

// Старый способ копирования
const fallbackCopy = (textarea: HTMLTextAreaElement) => {
  try {
    const successful = document.execCommand('copy');
    if (successful) {
      showCopySuccess();
    } else {
      throw new Error('Не удалось выполнить команду копирования');
    }
  } catch (err) {
    throw err;
  }
};

// Показываем уведомление об успешном копировании
const showCopySuccess = () => {
  // Используем native Telegram WebApp API если доступен
  if (window.Telegram && window.Telegram.WebApp) {
    window.Telegram.WebApp.showAlert('Текст скопирован в буфер обмена!');
  } else {
    alert('Текст скопирован в буфер обмена!');
  }
};

onMounted(async () => {
  try {
    if (!userStore.userData) {
      await userStore.loadUserData();
    }

    const userId = userStore.userData.id;
    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/user/appeals/?user_id=${userId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Ошибка при получении данных.');
    }

    appeals.value = await response.json();
  } catch (error) {
    console.error('Ошибка:', error.message);
    await router.push(`/error?message=${encodeURIComponent(error.message)}`);
  } finally {
    isLoading.value = false;
  }
});

const openModal = (text: string) => {
  selectedAppealText.value = text;
  isModalOpen.value = true;
};

const closeModal = () => {
  isModalOpen.value = false;
};

const truncateText = (text: string, maxLength: number = 50): string => {
  if (text.length > maxLength) {
    return text.slice(0, maxLength) + '...';
  }
  return text;
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${day}.${month}.${year} ${hours}:${minutes}`;
};
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-4">
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Мои заявки
    </h1>

    <div v-if="isLoading" class="text-gray-400">
      Загрузка данных...
    </div>

    <div v-else-if="appeals.length > 0" class="w-full max-w-7xl bg-gray-800 shadow-lg rounded-lg overflow-hidden">
      <!-- Обертка для таблицы с горизонтальной прокруткой -->
      <div class="overflow-x-auto">
        <table class="w-full text-sm text-left text-gray-400 min-w-max">
          <thead class="text-xs uppercase bg-gray-700 text-gray-300">
            <tr>
              <th scope="col" class="px-4 py-3">ID</th>
              <th scope="col" class="px-4 py-3">Текст заявки</th>
              <th scope="col" class="px-4 py-3">Комиссия</th>
              <th scope="col" class="px-4 py-3">Создано</th>
              <th scope="col" class="px-4 py-3">Обновлено</th>
              <th scope="col" class="px-4 py-3">Контактная информация</th>
              <th scope="col" class="px-4 py-3">Файл</th>
              <th scope="col" class="px-4 py-3">Статус</th>
              <th scope="col" class="px-4 py-3">Действия</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="appeal in appeals" :key="appeal.id" class="border-b border-gray-700 hover:bg-gray-700">
              <td class="px-4 py-4">{{ appeal.id }}</td>
              <td
                class="px-4 py-4 max-w-[200px] break-words whitespace-normal cursor-pointer text-blue-400 hover:text-blue-300 transition-colors duration-200"
                @click="openModal(appeal.appeal_text)"
              >
                {{ truncateText(appeal.appeal_text) }}
              </td>
              <td class="px-4 py-4 max-w-[150px] overflow-hidden text-ellipsis whitespace-nowrap">
                {{ appeal.commission_name || 'Нет комиссии' }}
              </td>
              <td class="px-4 py-4">{{ formatDate(appeal.created_at) }}</td>
              <td class="px-4 py-4">{{ formatDate(appeal.updated_at) }}</td>
              <td class="px-4 py-4 max-w-[150px] overflow-hidden text-ellipsis whitespace-nowrap">
                {{ appeal.contact_info || '-' }}
              </td>
              <td class="px-4 py-4">
                <a
                  v-if="appeal.file_path"
                  :href="`${configStore.backendBaseUrl}/api/v1/service/download/${appeal.id}`"
                  class="text-blue-400 hover:text-blue-300 transition-colors duration-200"
                  target="_blank"
                >
                  Скачать файл
                </a>
                <span v-else>Нет файла</span>
              </td>
              <td class="px-4 py-4">{{ getStatusDisplay(appeal.status) }}</td>
              <td class="px-4 py-4">
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
    </div>

    <div v-else class="text-gray-400">
      Нет данных для отображения.
    </div>

    <!-- Модальное окно -->
    <div v-if="isModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-gray-800 text-white p-6 rounded-lg w-11/12 md:w-3/4 lg:w-1/2 max-h-[80vh] overflow-y-auto relative">
        <!-- Кнопка закрытия в правом верхнем углу -->
        <button
          @click="closeModal"
          class="absolute top-4 right-4 text-red-500 hover:text-red-600 transition-colors duration-200"
        >
          &#x2715; <!-- Крестик -->
        </button>
        <h2 class="text-xl font-bold mb-4">Полный текст обращения</h2>
        <p class="text-gray-300 whitespace-pre-wrap break-words leading-relaxed">{{ selectedAppealText }}</p>
        <!-- Кнопка "Скопировать" -->
        <button
          @click="copyToClipboard(selectedAppealText)"
          class="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors duration-200"
        >
          Скопировать текст
        </button>
      </div>
    </div>
  </div>
</template>