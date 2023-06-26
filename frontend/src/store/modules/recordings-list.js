import RecordingListItem from '@/models/recording-list-item';
import RecordingService from '@/services/recordings.service';

export const namespaced = true;

export const state = {
    recordingsList: null
};

export const mutations = {
    SET_RECORDINGS_LIST(state, recordingsList) {
        state.recordingsList = recordingsList;
    },
    DELETE_RECORDING(state, id) {
        state.recordingsList = state.recordingsList.filter(function(obj) {
            return obj._id !== id;
        });
    },
    CLEAR_RECORDINGS_LIST(state) {
        state.recordingsList = null;
    }
};

export const actions = {
    getUserRecordings({ commit }, { filter_text, sort_by }) {
        return RecordingService.getAllRecordings(filter_text, sort_by).then(
            response => {
                let recordingsList = response.data.map(
                    val =>
                        new RecordingListItem(
                            val._id,
                            val.name,
                            val.created,
                            val.subject_full_name
                        )
                );
                commit('SET_RECORDINGS_LIST', recordingsList);
                return Promise.resolve(response);
            },
            error => {
                return Promise.reject(error);
            }
        );
    },
    deleteRecording({ commit }, { _id }) {
        return RecordingService.deleteRecordingById(_id).then(
            response => {
                commit('DELETE_RECORDING', _id);
                return Promise.resolve(response);
            },
            error => {
                return Promise.reject(error);
            }
        );
    },
    clearUserRecordings({ commit }) {
        commit('CLEAR_RECORDINGS_LIST');
    }
};
