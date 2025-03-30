import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    userData: null as any | null, // Данные пользователя
    authToken: null as string | null, // Токен авторизации
  }),
  actions: {
    setUserData(data: any) {
      this.userData = data;
    },
    setAuthToken(token: string) {
      this.authToken = token;
    },
    clearUserData() {
      this.userData = null;
      this.authToken = null;
      localStorage.removeItem('authToken'); // Удаляем токен из localStorage
    },
    async loadUserData() {
      if (!this.authToken) {
        console.error('Токен отсутствует.');
        return;
      }

      try {
        const response = await fetch(`http://localhost:8000/telegram_bot/get_user_data/${this.authToken}/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Ошибка при загрузке данных пользователя.');
        }

        const userData = await response.json();
        this.setUserData(userData); // Сохраняем данные пользователя
      } catch (error) {
        console.error('Ошибка при загрузке данных пользователя:', error.message);
        this.clearUserData(); // Очищаем данные, если произошла ошибка
      }
    },
  },
});