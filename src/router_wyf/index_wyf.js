import Vue from 'vue';
import Router from 'vue-router';
import UserWYF from '@/components_wyf/User_wyf/User_wyf.vue';
import ShopWYF from '@/components_wyf/Shop_wyf/Shop_wyf.vue';
import RiderWYF from '@/components_wyf/Rider_wyf/Rider_wyf.vue';
import Login_wyf from '@/components_wyf/Login_wyf.vue';

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/user',
      name: 'UserWYF',
      component: UserWYF
    },
    {
      path: '/shop',
      name: 'ShopWYF',
      component: ShopWYF
    },
    {
      path: '/rider',
      name: 'RiderWYF',
      component: RiderWYF
    },
    {
      path: '/',
      name: 'Login',
      component: Login_wyf
    }
  ]
});