<template>
    <v-app>
        <app-navigation />

        <v-main>
            <router-view></router-view>
        </v-main>

        <app-footer />
    </v-app>
</template>

<script>
import axios from 'axios';

import AppFooter from '@/components/AppFooter';
import AppNavigation from '@/components/AppNavigation';

export default {
    name: 'App',
    metaInfo() {
        return {
            title: 'EEG Assistant application',
            meta: [
                {
                    name: 'description',
                    content:
                        'EEG Assistant helps to automatize EEG classification.'
                },
                {
                    property: 'og:title',
                    content:
                        'EEG Assistant - Upload and analyse your EEG recordings.'
                },
                { property: 'og:site_name', content: 'EEG Assistant' },
                { property: 'og:type', content: 'website' },
                { name: 'robots', content: 'index,follow' }
            ]
        };
    },
    components: {
        AppFooter,
        AppNavigation
    },
    created() {
        const userString = localStorage.getItem('user');

        if (userString) {
            const userData = JSON.parse(userString);
            this.$store.commit('auth/LOGIN_SET_USER_DATA', userData);
        }
        axios.interceptors.response.use(undefined, function(err) {
            return new Promise(function() {
                if (err.status === 401) {
                    this.$store.dispatch('auth/logout');
                    this.$router.push('/sign-in');
                } else if (err.status === 500) {
                    this.$router.push('/network-issues');
                }
                throw err;
            });
        });
    }
};
</script>

<style></style>
