import api from '@/services/api';

const resource = '/auth';

export default {
    login(userFormData) {
        return api.post(`${resource}/token`, userFormData);
    }
};
