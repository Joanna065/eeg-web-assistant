import UserService from '@/services/user.service';

export const namespaced = true;

export const state = {
    currentUser: null,
    showUpdateSuccessAlert: false
};

export const mutations = {
    GET_CURRENT_USER_DATA(state, userData) {
        state.currentUser = userData;
    },
    UPDATE_PERSONAL_INFO(state, editData) {
        state.currentUser.first_name = editData.first_name
            ? editData.first_name
            : state.currentUser.first_name;
        state.currentUser.last_name = editData.last_name
            ? editData.last_name
            : state.currentUser.last_name;
        state.currentUser.email = editData.email
            ? editData.email
            : state.currentUser.email;
    },
    ERASE_CURRENT_USER(state) {
        state.currentUser = null;
        state.showUpdateSuccessAlert = false;
    },
    SET_UPDATE_ALERT(state, flag) {
        state.showUpdateSuccessAlert = flag;
    }
};

export const actions = {
    changeUpdateAlertValue({ commit }, value) {
        commit('SET_UPDATE_ALERT', value);
    },
    clearCurrentUserAccountData({ commit }) {
        commit('ERASE_CURRENT_USER');
    },
    createUser(state, { first_name, last_name, email, username, password }) {
        return UserService.createUser({
            first_name,
            last_name,
            email,
            username,
            password
        }).then(
            response => {
                return Promise.resolve(response);
            },
            error => {
                return Promise.reject(error);
            }
        );
    },
    getCurrentUser({ commit }) {
        return UserService.getCurrentUser().then(
            response => {
                commit('GET_CURRENT_USER_DATA', response.data);
                return Promise.resolve(response);
            },
            error => {
                return Promise.reject(error);
            }
        );
    },
    updateUserPersonalInfo({ commit }, { first_name, last_name, email }) {
        return UserService.updateUserPersonalInfo({
            first_name,
            last_name,
            email
        }).then(
            response => {
                commit('UPDATE_PERSONAL_INFO', {
                    first_name,
                    last_name,
                    email
                });
                return Promise.resolve(response);
            },
            error => {
                return Promise.reject(error);
            }
        );
    },
    updateUserPassword(state, { current_password, new_password }) {
        return UserService.updateUserPassword({
            current_password,
            new_password
        }).then(
            response => {
                return Promise.resolve(response);
            },
            error => {
                console.log(error.response.data);
                return Promise.reject(error);
            }
        );
    },
    deleteUserAccount({ commit }) {
        return UserService.deleteUser().then(
            response => {
                commit('ERASE_CURRENT_USER');
                return Promise.resolve(response);
            },
            error => {
                return Promise.reject(error);
            }
        );
    }
};
