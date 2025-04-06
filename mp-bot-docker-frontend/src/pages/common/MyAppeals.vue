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
    const userId = userStore.userData.user_id; // Получаем user_id из хранилища
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
            <td class="px-6 py-4 max-w-[300px] break-words whitespace-normal">
              {{ appeal.appeal_text }}
            </td>
            <td class="px-6 py-4">{{ appeal.contact_info || '-' }}</td>
            <td class="px-6 py-4">
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