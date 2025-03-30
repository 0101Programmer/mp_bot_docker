import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router';
import { createPinia } from 'pinia';
import { useUserStore } from './stores/userStore'; // Импортируем хранилище

const app = createApp(App);

// Подключаем Pinia
const pinia = createPinia();
app.use(pinia);

// Проверяем, есть ли токен в localStorage
const authToken = localStorage.getItem('authToken');
if (authToken) {
  const userStore = useUserStore();
  userStore.setAuthToken(authToken);

  // Обрабатываем Promise с await
  (async () => {
    try {
      await userStore.loadUserData(); // Загружаем данные пользователя
    } catch (error) {
      console.error('Ошибка при загрузке данных пользователя:', error.message);
    }
  })();
}

// Подключаем маршрутизацию
app.use(router);

app.mount('#app');
