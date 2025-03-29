import { createRouter, createWebHistory } from 'vue-router';
import Account from '../pages/Account.vue';
import ErrorPage from '../pages/ErrorPage.vue';

const routes = [
  { path: '/account', component: Account },
  { path: '/error', component: ErrorPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;