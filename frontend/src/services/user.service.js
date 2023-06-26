import api from '@/services/api';

const resource = '/user';

export default {
    getCurrentUser() {
        return api.get(`${resource}`);
    },

    createUser(newUser) {
        return api.post(`${resource}`, newUser);
    },

    updateUserPassword(updatePasswordData) {
        return api.patch(`${resource}/password`, updatePasswordData);
    },

    updateUserPersonalInfo(updateData) {
        return api.patch(`${resource}/personal_info`, updateData);
    },

    deleteUser() {
        return api.delete(`${resource}`);
    }
};
