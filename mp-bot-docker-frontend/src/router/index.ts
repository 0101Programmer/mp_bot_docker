import { createRouter, createWebHistory } from 'vue-router';
import Account from '../pages/Account.vue';
import ErrorPage from '../pages/ErrorPage.vue';
import Home from '../pages/Home.vue';
import MyAppeals from "../pages/MyAppeals.vue";
import Success from "../pages/Success.vue";


const routes = [
  { path: '/account', component: Account },
  { path: '/error', component: ErrorPage },
  { path: '/', component: Home },
  { path: '/my_appeals', component: MyAppeals },
  {
  path: '/success',
  name: 'Success',
  component: Success,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;