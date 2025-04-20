import { createApp } from 'vue';
import './style.css';
import App from './App.vue';
import router from './router';
import { createPinia } from 'pinia';

const app = createApp(App);

// Подключаем Pinia
const pinia = createPinia();
app.use(pinia);

// Подключаем маршрутизацию
app.use(router);

// Монтируем приложение
app.mount('#app');