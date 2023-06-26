import Vue from 'vue';
import VueRouter from 'vue-router';

import Home from '@/views/Home.vue';

Vue.use(VueRouter);

const routes = [
    {
        path: '/',
        name: 'Home',
        component: Home
    },
    {
        path: '/about',
        name: 'About',
        component: () => import('@/views/About.vue')
    },
    {
        path: '/sign-in',
        name: 'SignIn',
        component: () => import('@/views/SignIn.vue')
    },
    {
        path: '/sign-up',
        name: 'SignUp',
        component: () => import('@/views/SignUp.vue')
    },
    {
        path: '/sign-up-success',
        name: 'SignUpSuccess',
        component: () => import('@/views/SignUpSuccess.vue')
    },
    {
        path: '/my-recordings',
        name: 'MyRecordings',
        component: () => import('@/views/UserRecordings.vue'),
        meta: {
            requiresAuth: true
        }
    },
    {
        path: '/account-settings',
        name: 'AccountSettings',
        component: () => import('@/views/AccountSettings.vue'),
        meta: {
            requiresAuth: true
        }
    },
    {
        path: '/analysis/:id',
        name: 'Analysis',
        component: () => import('@/views/Analysis.vue'),
        props: true,
        meta: {
            requiresAuth: true
        }
    },
    {
        path: '/403-forbidden',
        name: '403',
        component: () => import('@/views/ForbiddenAccess.vue')
    },
    {
        path: '/404',
        name: '404',
        component: () => import('@/views/NotFound.vue'),
        props: true
    },
    {
        path: '/network-issues',
        name: 'NetworkIssue',
        component: () => import('@/views/NetworkIssue.vue')
    },
    {
        path: '*',
        redirect: { name: '404', params: { resource: 'page' } }
    }
];

const router = new VueRouter({
    mode: 'history',
    base: process.env.BASE_URL,
    scrollBehavior() {
        return { x: 0, y: 0 };
    },
    routes
});

router.beforeEach((to, from, next) => {
    const loggedIn = localStorage.getItem('user');

    if (to.matched.some(record => record.meta.requiresAuth) && !loggedIn) {
        next('/sign-in');
    } else {
        next();
    }
});

export default router;
