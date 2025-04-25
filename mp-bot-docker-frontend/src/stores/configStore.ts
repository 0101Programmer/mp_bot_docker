import { defineStore } from 'pinia';

export const useConfigStore = defineStore('config', {
  state: () => ({
    backendBaseUrl: import.meta.env.VITE_BACKEND_BASE_URL,
    minTxtLength: parseInt(import.meta.env.VITE_MIN_TXT_LENGTH),
    maxTxtLength: parseInt(import.meta.env.VITE_MAX_TXT_LENGTH),
    maxFileSizeMb: parseInt(import.meta.env.VITE_MAX_FILE_SIZE) / (1024 * 1024),
  }),
});