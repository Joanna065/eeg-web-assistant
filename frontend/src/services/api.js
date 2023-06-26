import axios from 'axios';

import router from '@/router/index';
import store from '@/store/index';

const baseUrl = process.env.VUE_APP_BASE_URL_API;

const api = axios.create({
    baseURL: baseUrl,
    timeout: 60000
});

api.interceptors.response.use(undefined, function(err) {
    return new Promise(function() {
        if (err.status === 401) {
            store.dispatch('auth/logout');
            router.push('/sign-in');
        } else if (err.status === 403) {
            router.push('/403-forbidden');
        } else if (err.status === 500) {
            router.push('/network-issues');
        }
        throw err;
    });
});

export default api;
