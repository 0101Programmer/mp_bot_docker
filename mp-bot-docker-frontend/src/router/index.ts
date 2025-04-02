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
import UpdateCommission from "../pages/admin/commissions/UpdateCommission.vue";
import GetUpdateDeleteAppeal from "../pages/admin/appeals/GetUpdateDeleteAppeal.vue";
import GetUpdateDeleteRequest from "../pages/admin/admin_requests/GetUpdateDeleteRequest.vue";


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
  {
  path: '/edit_commission/:id',
  name: 'UpdateCommission',
  component: UpdateCommission
  },
  {
  path: '/get_update_delete_appeal',
  name: 'GetUpdateDeleteAppeal',
  component: GetUpdateDeleteAppeal
  },
  {
  path: '/get_update_delete_admin_requests',
  name: 'GetUpdateDeleteRequest',
  component: GetUpdateDeleteRequest
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;