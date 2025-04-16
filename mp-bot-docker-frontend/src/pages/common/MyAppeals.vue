<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useUserStore } from '@/stores/userStore.ts';
import { useRouter } from 'vue-router';
import { useConfigStore } from '@/stores/configStore.ts'; // Импортируем хранилище конфигурации

// Инициализируем хранилище и роутер
const userStore = useUserStore();
const configStore = useConfigStore(); // Получаем доступ к хранилищу конфигурации
const router = useRouter();

// Состояние для загрузки данных
const isLoading = ref(true);
const appeals = ref([]);

// Состояние для модального окна
const isModalOpen = ref(false); // Открыто ли модальное окно
const selectedAppealText = ref(''); // Текст выбранного обращения

// Функция для преобразования статуса в русский текст
const getStatusDisplay = (status: string) => {
  const statusMap = {
    'new': 'Новое',
    'processed': 'Обработано',
    'rejected': 'Отклонено'
  };
  return statusMap[status] || status;
};

// Функция для подтверждения удаления
const confirmDelete = (appealId: number) => {
  const isConfirmed = confirm(
    "Удаление обращения очистит всю его историю, а также отзовёт его, в случае, если оно не было обработано. Вы уверены?"
  );
  if (isConfirmed) {
    deleteAppeal(appealId);
  }
};

// Функция для удаления обращения
const deleteAppeal = async (appealId: number) => {
  try {
    // Получаем user_id из хранилища
    const userId = userStore.userData?.id;
    if (!userId) {
      throw new Error('User ID не найден.');
    }

    // Отправляем запрос на удаление с user_id
    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/user/appeal/${appealId}/delete/?user_id=${userId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Ошибка при удалении обращения.');
    }

    // Удаляем обращение из списка на фронтенде
    appeals.value = appeals.value.filter((appeal) => appeal.id !== appealId);
  } catch (error) {
    console.error('Ошибка:', error.message);
    alert(`Ошибка при удалении обращения: ${error.message}`);
  }
};

// Функция для загрузки данных через API
onMounted(async () => {
  try {
    // Если токена нет, перенаправляем на страницу ошибки
    if (!userStore.authToken) {
      throw new Error('Токен отсутствует. Пожалуйста, авторизуйтесь.');
    }

    // Если данные пользователя отсутствуют, загружаем их
    if (!userStore.userData) {
      await userStore.loadUserData();
    }

    // Загружаем список обращений
    const userId = userStore.userData.id; // Получаем user_id из хранилища
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
    isLoading.value = false; // Завершаем загрузку
  }
});

// Функция для открытия модального окна
const openModal = (text: string) => {
  selectedAppealText.value = text; // Устанавливаем текст для модального окна
  isModalOpen.value = true; // Открываем модальное окно
};

// Функция для закрытия модального окна
const closeModal = () => {
  isModalOpen.value = false; // Закрываем модальное окно
};

// Функция для обрезания текста
const truncateText = (text: string, maxLength: number = 50): string => {
  if (text.length > maxLength) {
    return text.slice(0, maxLength) + '...';
  }
  return text;
};

// Функция для форматирования даты
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${day}.${month}.${year} ${hours}:${minutes}`;
};

// Метод для копирования текста
const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text).then(() => {
    alert('Текст скопирован в буфер обмена!');
  }).catch((error) => {
    console.error('Ошибка при копировании текста:', error);
    alert('Не удалось скопировать текст.');
  });
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