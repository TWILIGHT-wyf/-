import Vue from 'vue';
import App from './App_wyf.vue';
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import router from '@/router_wyf/index_wyf';
import axios from '@/api/index';

Vue.use(ElementUI);
Vue.config.productionTip = false;
Vue.prototype.$axios = axios;

new Vue({
  router,
  render: h => h(App),
}).$mount('#app');