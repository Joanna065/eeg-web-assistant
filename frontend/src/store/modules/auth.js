import api from '@/services/api';
import AuthService from '@/services/auth.service';

export const namespaced = true;

export const state = {
    user: null
};

const getToken = () => {
    const userSession = JSON.parse(localStorage.getItem('user'));
    return userSession && userSession.access_token;
};

export const mutations = {
    LOGIN_SET_USER_DATA(state, userData) {
        localStorage.setItem('user', JSON.stringify(userData));
        state.user = userData;
        api.defaults.headers.common['Authorization'] = `Bearer ${getToken()}`;
    },
    SET_USER_LOGIN_FAILURE(state) {
        state.user = null;
    },
    LOGOUT_CLEAR_USER(state) {
        state.user = null;
        localStorage.removeItem('user');
        api.defaults.headers.common['Authorization'] = '';
    }
};

export const actions = {
    login({ commit }, formData) {
        return AuthService.login(formData).then(
            response => {
                commit('LOGIN_SET_USER_DATA', response.data);
                return Promise.resolve(response);
            },
            error => {
                commit('SET_USER_LOGIN_FAILURE');
                return Promise.reject(error);
            }
        );
    },
    logout({ commit, dispatch }) {
        commit('LOGOUT_CLEAR_USER');
        dispatch('userAccount/clearCurrentUserAccountData', null, {
            root: true
        });
        dispatch('recordingsList/clearUserRecordings', null, { root: true });
        dispatch('classification/clearClassificationData', null, {
            root: true
        });
    }
};

export const getters = {
    loggedIn(state) {
        return !!state.user;
    },
    loggedUsername(state) {
        if (state.user && state.user.username) {
            return state.user.username;
        } else {
            return '';
        }
    }
};
