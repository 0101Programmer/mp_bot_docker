<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useUserStore } from '../stores/userStore';
import { useRouter } from 'vue-router';

// Инициализируем хранилище и роутер
const userStore = useUserStore();
const router = useRouter();

// Состояние для загрузки данных
const isLoading = ref(true);
const appeals = ref([]);

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
    const userId = userStore.userData?.user_id;
    if (!userId) {
      throw new Error('User ID не найден.');
    }

    // Отправляем запрос на удаление с user_id
    const response = await fetch(`http://localhost:8000/telegram_bot/appeal/${appealId}/delete/?user_id=${userId}`, {
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

// Проверяем, есть ли данные пользователя в хранилище
if (!userStore.userData) {
  console.error('Данные пользователя не найдены.');
  router.push('/error?message=Данные пользователя не найдены');
}

// Функция для загрузки данных через API
onMounted(() => {
  const userId = userStore.userData.user_id; // Получаем user_id из хранилища
  fetch(`http://localhost:8000/telegram_bot/appeals/?user_id=${userId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error('Ошибка при получении данных.');
      }
      return response.json();
    })
    .then((data) => {
      appeals.value = data;
    })
    .catch((error) => {
      console.error('Ошибка:', error.message);
      router.push(`/error?message=${encodeURIComponent(error.message)}`);
    })
    .finally(() => {
      isLoading.value = false;
    });
});
</script>
<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-4">
    <!-- Приветственное сообщение -->
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Мои заявки
    </h1>

    <!-- Если данные загружаются -->
    <div v-if="isLoading" class="text-gray-400">
      Загрузка данных...
    </div>

    <!-- Если данные загружены -->
    <div v-else-if="appeals.length > 0" class="w-full max-w-4xl bg-gray-800 shadow-lg rounded-lg overflow-hidden">
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
          <tr v-for="appeal in appeals" :key="appeal.id" class="border-b border-gray-700 hover:bg-gray-700">
            <td class="px-6 py-4">{{ appeal.id }}</td>
            <td class="px-6 py-4">{{ appeal.appeal_text }}</td>
            <td class="px-6 py-4">{{ appeal.contact_info || '-' }}</td>
            <td class="px-6 py-4">
              <a
                v-if="appeal.file_path"
                :href="`http://localhost:8000/telegram_bot/download/${appeal.file_path.split('/').pop()}`"
                class="text-blue-400 hover:text-blue-300 transition-colors duration-200"
                target="_blank"
              >
                Скачать файл
              </a>
              <span v-else>Нет файла</span>
            </td>
            <td class="px-6 py-4">{{ appeal.status }}</td>
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