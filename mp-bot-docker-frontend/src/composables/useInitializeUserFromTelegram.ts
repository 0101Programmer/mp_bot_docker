import { onMounted } from 'vue';
import { useUserStore } from '@/stores/userStore';

export function useInitializeUserFromTelegram() {
  const userStore = useUserStore();

  onMounted(() => {
    // Проверяем, доступен ли объект Telegram WebApp
    if (window.Telegram && window.Telegram.WebApp) {
      const initData = window.Telegram.WebApp.initDataUnsafe;

      if (initData && initData.user) {
        const { id, username } = initData.user;

        // Сохраняем данные в хранилище
        userStore.setUser(username || 'Гость', id);
      } else {
        console.error('Telegram WebApp initDataUnsafe does not contain user data.');
      }
    } else {
      console.error('Telegram WebApp is not available.');
    }
  });
}