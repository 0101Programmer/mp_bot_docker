<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-start p-4">
    <!-- Приветственное сообщение -->
    <h1 class="text-3xl font-bold text-blue-400 mt-8 mb-6 text-center">
      Панель администратора
    </h1>

    <!-- Если пользователь администратор -->
    <div v-if="isAdmin" class="w-full max-w-2xl bg-gray-800 shadow-lg rounded-lg overflow-hidden p-6">
      <h2 class="text-xl font-bold text-blue-400 mb-4">Доступные действия:</h2>
      <ul class="space-y-3">
        <!-- Выпадающий список для действий с комиссиями -->
        <li>
          <details class="block w-full">
            <summary class="px-4 py-2 bg-gray-700 hover:bg-gray-800 text-white font-semibold rounded-md transition-colors duration-200 cursor-pointer">
              Действия с комиссиями
            </summary>
            <ul class="mt-2 space-y-2 pl-4">
              <li>
                <a href="/create_commission" class="block px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-md transition-colors duration-200">
                  Создать комиссию
                </a>
              </li>
              <li>
                <a href="/delete_commission" class="block px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-md transition-colors duration-200">
                  Удалить комиссию
                </a>
              </li>
              <li>
                <a href="#" @click.prevent="openModal" class="block px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-md transition-colors duration-200">
                  Редактировать комиссию
                </a>
              </li>
            </ul>
          </details>
        </li>
        <li>
          <a href="#" @click.prevent="openDeleteUserModal" class="block w-full px-4 py-2 bg-gray-700 hover:bg-gray-800 text-white font-semibold rounded-md transition-colors duration-200">
            Удалить пользователя
          </a>
        </li>
        <li>
          <a href="/get_update_delete_appeal" class="block w-full px-4 py-2 bg-gray-700 hover:bg-gray-800 text-white font-semibold rounded-md transition-colors duration-200">
            Просмотр обращений
          </a>
        </li>
        <li>
          <a href="/get_update_delete_admin_requests" class="block w-full px-4 py-2 bg-gray-700 hover:bg-gray-800 text-white font-semibold rounded-md transition-colors duration-200">
            Заявки на получение прав администратора
          </a>
        </li>
      </ul>
    </div>

    <!-- Если пользователь НЕ администратор -->
    <div v-else class="w-full max-w-2xl bg-gray-800 shadow-lg rounded-lg overflow-hidden p-6 text-center">
      <p class="text-gray-400 text-lg mb-4">
        У вас нет прав администратора.
      </p>
      <p class="text-gray-500 text-sm">
        Вы можете
        <a href="/sent_admin_request" class="text-blue-400 underline hover:text-blue-500 transition-colors duration-200">
          заполнить форму
        </a>
        на получение прав администратора.
      </p>
    </div>

    <!-- Модальное окно для редактирования комиссии -->
    <div v-if="isModalOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-gray-800 p-6 rounded-lg shadow-lg w-full max-w-md">
        <h2 class="text-xl font-bold text-blue-400 mb-4">Выберите комиссию для редактирования</h2>

        <!-- Выбор комиссии из выпадающего списка -->
        <div class="mb-4">
          <label for="commission_select" class="block text-sm font-medium text-gray-300">Выберите комиссию</label>
          <select
            id="commission_select"
            v-model="selectedCommissionId"
            class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="" disabled selected>Выберите комиссию</option>
            <option v-for="commission in commissions" :key="commission.id" :value="commission.id">
              {{ commission.name }}
            </option>
          </select>
        </div>

        <!-- Ввод ID комиссии -->
        <div class="mb-4">
          <label for="commission_id" class="block text-sm font-medium text-gray-300">Или введите ID комиссии</label>
          <input
            id="commission_id"
            v-model="manualCommissionId"
            type="number"
            class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Введите ID комиссии"
          />
        </div>

        <!-- Кнопки модального окна -->
        <div class="flex justify-end space-x-2">
          <button
            @click="closeModal"
            class="px-4 py-2 bg-gray-600 text-white font-semibold rounded-md hover:bg-gray-700 transition-colors duration-200"
          >
            Отмена
          </button>
          <button
            @click="redirectToEditPage"
            class="px-4 py-2 bg-blue-500 text-white font-semibold rounded-md hover:bg-blue-600 transition-colors duration-200"
          >
            Перейти к редактированию
          </button>
        </div>
      </div>
    </div>

    <!-- Модальное окно для удаления пользователя -->
    <div v-if="isDeleteUserModalOpen" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div class="bg-gray-800 p-6 rounded-lg shadow-lg w-full max-w-md">
        <h2 class="text-xl font-bold text-red-400 mb-4">Удаление пользователя</h2>

        <!-- Ввод ID пользователя -->
        <div class="mb-4">
          <label for="user_id" class="block text-sm font-medium text-gray-300">Введите ID пользователя</label>
          <input
            id="user_id"
            v-model.number="manualUserId"
            type="number"
            class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-red-500"
            placeholder="Введите ID пользователя"
          />
        </div>

        <!-- Кнопки модального окна -->
        <div class="flex justify-end space-x-2">
          <button
            @click="closeDeleteUserModal"
            class="px-4 py-2 bg-gray-600 text-white font-semibold rounded-md hover:bg-gray-700 transition-colors duration-200"
          >
            Отмена
          </button>
          <button
            @click="deleteUser"
            class="px-4 py-2 bg-red-500 text-white font-semibold rounded-md hover:bg-red-600 transition-colors duration-200"
          >
            Удалить пользователя
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/userStore.ts';
import { useConfigStore } from '@/stores/configStore.ts'; // Импортируем хранилище конфигурации

// Инициализируем хранилище пользователя, конфигурации и роутер
const userStore = useUserStore();
const configStore = useConfigStore(); // Получаем доступ к хранилищу конфигурации
const router = useRouter();

// Проверка, является ли пользователь администратором
const isAdmin = computed(() => userStore.userData?.is_admin || false);

// Состояния для модального окна редактирования комиссии
const commissions = ref<{ id: string; name: string }[]>([]);
const selectedCommissionId = ref<string | null>(null);
const manualCommissionId = ref<string>('');
const isModalOpen = ref(false);

// Состояния для модального окна удаления пользователя
const isDeleteUserModalOpen = ref(false);
const manualUserId = ref<number | null>(null); // ID пользователя теперь число

// Загрузка списка комиссий
onMounted(async () => {
  try {
    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/service/commissions/`); // Используем backendBaseUrl
    if (response.ok) {
      commissions.value = await response.json();
    } else {
      console.error('Ошибка при загрузке комиссий');
    }
  } catch (error) {
    console.error('Ошибка сети:', error);
  }
});

// Открытие модального окна для редактирования комиссии
const openModal = () => {
  isModalOpen.value = true;
};

// Закрытие модального окна для редактирования комиссии
const closeModal = () => {
  isModalOpen.value = false;
};

// Переход на страницу редактирования комиссии
const redirectToEditPage = () => {
  const commissionId = selectedCommissionId.value || manualCommissionId.value;
  if (!commissionId) {
    alert('Пожалуйста, выберите комиссию или введите её ID.');
    return;
  }

  // Перенаправляем на страницу редактирования
  router.push(`/edit_commission/${commissionId}`);
  closeModal();
};

// Открытие модального окна для удаления пользователя
const openDeleteUserModal = () => {
  isDeleteUserModalOpen.value = true;
};

// Закрытие модального окна для удаления пользователя
const closeDeleteUserModal = () => {
  isDeleteUserModalOpen.value = false;
};

// Удаление пользователя
const deleteUser = async () => {
  const userId = manualUserId.value; // ID пользователя уже число
  if (!userId) {
    alert('Пожалуйста, введите ID пользователя.');
    return;
  }

  try {
    const response = await fetch(`${configStore.backendBaseUrl}/api/v1/admin/delete_user/${userId}/`, { // Используем backendBaseUrl
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        admin_id: userStore.userData?.id,
      }),
    });

    if (response.ok) {
      alert('Пользователь успешно удален.');
      closeDeleteUserModal();
    } else {
      const errorData = await response.json(); // Извлекаем данные об ошибке
      const errorMessage = errorData.detail || errorData.message || 'Произошла ошибка при удалении пользователя.';
      alert(errorMessage); // Выводим конкретное сообщение об ошибке
    }
  } catch (error) {
    console.error('Ошибка:', error.message);
    alert(`Ошибка при удалении пользователя: ${error.message}`);
  }
};
</script>