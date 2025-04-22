import { defineStore } from 'pinia';
import axios from 'axios';
import { useConfigStore } from './configStore';

export const useUserStore = defineStore('user', {
  state: () => ({
    username: null as string | null,
    telegramId: null as number | null,
    isLoggedIn: false,
    databaseData: null as any | null, // Дополнительные данные из БД
  }),
  actions: {
    setUser(username: string, telegramId: number) {
      this.username = username;
      this.telegramId = telegramId;
      this.isLoggedIn = true;
    },
    clearUser() {
      this.username = null;
      this.telegramId = null;
      this.isLoggedIn = false;
      this.databaseData = null;
    },
    async loadUserDataFromBackend(telegramId: number) {
      if (!telegramId) {
        console.error('Telegram ID is not provided. Cannot load user data.');
        return;
      }

      const configStore = useConfigStore();
      if (!configStore.backendBaseUrl) {
        console.error('Backend base URL is not set. Cannot send request.');
        return;
      }

      try {
        console.log('Sending request to backend with telegramId:', telegramId);
        console.log('Request payload:', { telegramId }); // Логируем тело запроса

        const response = await axios.post(
          `${configStore.backendBaseUrl}/api/v1/service/get_user_data/`,
          { telegramId },
          {
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );

        console.log('Response from backend:', response.data);
        this.databaseData = response.data;
      } catch (error) {
        console.error('Failed to load user data from backend:', error);

        if (error.response) {
          console.error('Response data:', error.response.data); // Логируем ответ от сервера
          console.error('Response status:', error.response.status);
          console.error('Response headers:', error.response.headers);
        } else if (error.request) {
          console.error('No response received:', error.request);
        } else {
          console.error('Error message:', error.message);
        }
      }
    },
  },
});