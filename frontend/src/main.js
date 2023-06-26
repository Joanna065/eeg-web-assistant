import 'material-design-icons-iconfont/dist/material-design-icons.css';
import 'nprogress/nprogress.css';

import Vue from 'vue';

import App from './App.vue';
import vuetify from './plugins/vuetify';
import router from './router';
import store from './store';

Vue.config.productionTip = false;

new Vue({
    router,
    store,
    vuetify,
    render: h => h(App)
}).$mount('#app');
