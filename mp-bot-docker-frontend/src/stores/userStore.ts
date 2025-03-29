import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', {
  state: () => ({
    userData: null as any | null, // Данные пользователя
  }),
  actions: {
    setUserData(data: any) {
      this.userData = data;
    },
    clearUserData() {
      this.userData = null;
    },
  },
});