import { defineStore } from 'pinia';
import { useConfigStore } from './configStore';

export const useUserStore = defineStore('user', {
  state: () => ({
    userData: null as any | null,
    authToken: null as string | null,
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
      localStorage.removeItem('authToken');
    },
    async loadUserData() {
      if (!this.authToken) {
        console.error('Токен отсутствует.');
        return;
      }

      try {
        const configStore = useConfigStore();
        const backendUrl = `${configStore.backendBaseUrl}/get_user_data/${this.authToken}/`;

        const response = await fetch(backendUrl, {
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
        this.setUserData(userData);
      } catch (error) {
        console.error('Ошибка при загрузке данных пользователя:', error.message);
        this.clearUserData();
      }
    },
  },
});