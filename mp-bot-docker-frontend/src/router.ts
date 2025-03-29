import { createRouter, createWebHistory } from 'vue-router';
import Account from "./pages/Account.vue";

const routes = [
  { path: '/account', component: Account },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;