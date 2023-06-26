import '@mdi/font/css/materialdesignicons.css';

import Vue from 'vue';
import VueMeta from 'vue-meta';
import Vuetify from 'vuetify/lib';

Vue.use(Vuetify, VueMeta);

export default new Vuetify({
    icons: {
        iconfont: 'mdi'
    },
    theme: {
        themes: {
            light: {
                primary: '#1a237e',
                secondary: '#5c6bc0',
                accent: '#ffb300',
                error: '#f44336',
                warning: '#ff9800',
                info: '#90a4ae',
                success: '#4caf50'
            },
            dark: {
                primary: '#000051'
            }
        }
    }
});
