import RecordingService from '@/services/recordings.service';

export const namespaced = true;

export const state = {
    uploadedFileId: null
};

export const mutations = {
    SET_UPLOADED_FILE_ID(state, uploadedFileId) {
        state.uploadedFileId = uploadedFileId;
    },
    CLEAR_UPLOADED_FILE_ID(state) {
        state.uploadedFileId = null;
    }
};

export const actions = {
    uploadFile({ commit }, newRecordingData) {
        return RecordingService.createRecording(newRecordingData).then(
            response => {
                commit('SET_UPLOADED_FILE_ID', response.data);
                return Promise.resolve(response);
            },
            error => {
                return Promise.reject(error);
            }
        );
    },
    clearUploadedFile({ commit }) {
        commit('CLEAR_UPLOADED_FILE_ID');
    }
};
