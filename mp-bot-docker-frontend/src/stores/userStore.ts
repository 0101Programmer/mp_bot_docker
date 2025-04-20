import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    username: null as string | null,
    telegramId: null as number | null,
    isLoggedIn: false,
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
    },
  },
});