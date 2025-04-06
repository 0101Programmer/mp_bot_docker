import { defineStore } from 'pinia';
import { useConfigStore } from './configStore';
import axios from 'axios';

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
        const backendUrl = `${configStore.backendBaseUrl}/api/v1/service/get_user_data/${this.authToken}/`;

        const response = await axios.get(backendUrl, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        this.setUserData(response.data);
      } catch (error) {
        console.error('Ошибка при загрузке данных пользователя:', error.message || 'Неизвестная ошибка');
        this.clearUserData();
      }
    },
  },
});