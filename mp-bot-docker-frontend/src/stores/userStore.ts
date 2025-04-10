import { defineStore } from 'pinia';
import { useConfigStore } from './configStore';
import axios, { AxiosError } from 'axios';

interface UserData {
  id: number;
  telegram_id: number;
  username: string;
  first_name: string;
  last_name: string;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

export const useUserStore = defineStore('user', {
  state: () => ({
    userData: null as UserData | null,
    authToken: localStorage.getItem('authToken') || null,
  }),
  actions: {
    setUserData(data: UserData) {
      this.userData = data;
    },
    setAuthToken(token: string) {
      this.authToken = token;
      localStorage.setItem('authToken', token);
    },
    clearUserData() {
      this.userData = null;
      this.authToken = null;
      localStorage.removeItem('authToken');
    },
    getApiUrl(endpoint: string): string {
      const configStore = useConfigStore();
      return `${configStore.backendBaseUrl}/api/v1/service/${endpoint}`;
    },
    async loadUserData() {
      if (!this.authToken) {
        throw new Error('Токен отсутствует');
      }

      try {
        const backendUrl = this.getApiUrl(`get_user_data/${this.authToken}/`);

        const response = await axios.get(backendUrl, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        this.setUserData(response.data);
      } catch (error) {
        if (axios.isAxiosError(error) && error.response?.status === 401) {
          // Если токен недействителен, очищаем данные и выбрасываем ошибку
          this.clearUserData();
          throw new Error('Токен недействителен. Пожалуйста, авторизуйтесь заново.');
        }

        console.error('Ошибка при загрузке данных пользователя:', error.message || 'Неизвестная ошибка');
        this.clearUserData();
        throw error;
      }
    },
  },
});