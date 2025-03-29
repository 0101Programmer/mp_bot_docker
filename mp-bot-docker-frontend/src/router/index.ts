import { createRouter, createWebHistory } from 'vue-router';
import Account from '../pages/Account.vue';
import ErrorPage from '../pages/ErrorPage.vue';
import Home from '../pages/Home.vue';


const routes = [
  { path: '/account', component: Account },
  { path: '/error', component: ErrorPage },
  { path: '/', component: Home },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;