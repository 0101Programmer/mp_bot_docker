import { createRouter, createWebHistory } from 'vue-router';
import Account from '../pages/Account.vue';
import ErrorPage from '../pages/ErrorPage.vue';
import Home from '../pages/Home.vue';
import MyAppeals from "../pages/MyAppeals.vue";
import Success from "../pages/Success.vue";
import CreateAppeal from "../pages/CreateAppeal.vue";
import CommissionsInfo from "../pages/CommissionsInfo.vue";
import AdminPanel from "../pages/AdminPanel.vue";
import CreateCommission from "../pages/admin/commissions/CreateCommission.vue";
import DeleteCommission from "../pages/admin/commissions/DeleteCommission.vue";


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
  {
  path: '/create_appeal',
  name: 'CreateAppeal',
  component: CreateAppeal,
  },
  {
  path: '/commissions_info',
  name: 'CommissionsInfo',
  component: CommissionsInfo,
  },
  {
  path: '/admin_panel',
  name: 'AdminPanel',
  component: AdminPanel,
  },
  {
  path: '/create_commission',
  name: 'CreateCommission',
  component: CreateCommission
  },
  {
  path: '/delete_commission',
  name: 'DeleteCommission',
  component: DeleteCommission
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;