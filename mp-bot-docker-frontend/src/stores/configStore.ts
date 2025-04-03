import { defineStore } from 'pinia';

export const useConfigStore = defineStore('config', {
  state: () => ({
    backendBaseUrl: import.meta.env.VITE_BACKEND_BASE_URL,
  }),
  actions: {
    setBackendBaseUrl(url: string) {
      this.backendBaseUrl = url;
    },
  },
});