import RecordingAnalysis from '@/models/recording-analysis';
import RecordingService from '@/services/recordings.service';

const handMapper = {
    right: 1,
    left: 2,
    ambidextrous: 3
};

const sexMapper = {
    unknown: 0,
    male: 1,
    female: 2
};

export const namespaced = true;

export const state = {
    currentRecording: null,

    showUpdateSnackbar: false,
    snackbarText: null,
    snackbarColor: 'info'
};

export const mutations = {
    SET_UPDATE_SNACKBAR(state, { flag, text, color }) {
        state.showUpdateSnackbar = flag;
        state.snackbarText = text;
        state.snackbarColor = color;
    },
    SET_CURRENT_RECORDING(state, recording) {
        state.currentRecording = recording;
    },
    CLEAR_CURRENT_RECORDING(state) {
        state.currentRecording = null;
    },
    CHANGE_RECORDING(state, updateData) {
        const changedName = updateData?.name;
        const changedNotes = updateData?.notes;

        if (typeof changedName !== 'undefined' && changedName) {
            state.currentRecording.name = changedName;
        }
        if (typeof changedNotes !== 'undefined') {
            state.currentRecording.notes = changedNotes;
        }
    },
    CHANGE_RECORDING_SUBJECT(state, updateSubject) {
        const subjectLastName = updateSubject?.last_name;
        const subjectFirstName = updateSubject?.first_name;
        const subjectMiddleName = updateSubject?.middle_name;
        const subjectBirthday = updateSubject?.birthday;
        const subjectSex = updateSubject?.sex;
        const subjectHand = updateSubject?.hand;

        if (typeof subjectLastName !== 'undefined') {
            state.currentRecording.subjectLastName = subjectLastName;
        }
        if (typeof subjectFirstName !== 'undefined') {
            state.currentRecording.subjectFirstName = subjectFirstName;
        }
        if (typeof subjectMiddleName !== 'undefined') {
            state.currentRecording.subjectMiddleName = subjectMiddleName;
        }
        if (typeof subjectBirthday !== 'undefined') {
            state.currentRecording.subjectBirthday = subjectBirthday;
        }
        if (typeof subjectSex !== 'undefined') {
            state.currentRecording.subjectSex = subjectSex;
        }
        if (typeof subjectHand !== 'undefined') {
            state.currentRecording.subjectHand = subjectHand;
        }
    }
};

export const actions = {
    fetchRecording({ commit, dispatch }, id) {
        return RecordingService.getRecordingById(id).then(
            response => {
                let recording = new RecordingAnalysis(response.data);
                commit('SET_CURRENT_RECORDING', recording);

                if (response.data?.classification) {
                    dispatch(
                        'classification/addExistingClassification',
                        {
                            recordingClassifications:
                                response.data.classification
                        },
                        { root: true }
                    );
                }
                return Promise.resolve(response);
            },
            error => {
                return Promise.reject(error);
            }
        );
    },
    updateRecording({ commit }, { id, updateData }) {
        return RecordingService.updateRecordingById(id, updateData).then(
            response => {
                commit('CHANGE_RECORDING', updateData);
                return Promise.resolve(response);
            },
            error => {
                return Promise.reject(error);
            }
        );
    },
    updateRecordingSubject({ commit }, { id, updateSubject }) {
        return RecordingService.updateRecordingSubjectById(id, {
            first_name: updateSubject.first_name,
            last_name: updateSubject.last_name,
            middle_name: updateSubject.middle_name,
            birthday: updateSubject?.birthday
                ? Date.parse(updateSubject.birthday)
                : null,
            sex: updateSubject.sex ? sexMapper[updateSubject.sex] : null,
            hand: updateSubject?.hand ? handMapper[updateSubject.hand] : null
        }).then(
            response => {
                commit('CHANGE_RECORDING_SUBJECT', updateSubject);
                return Promise.resolve(response);
            },
            error => {
                return Promise.reject(error);
            }
        );
    },
    showSnackbar({ commit }, { flag, text, color }) {
        commit('SET_UPDATE_SNACKBAR', { flag, text, color });
    },
    clearAnalysisData({ commit }) {
        commit('CLEAR_CURRENT_RECORDING');
    }
};

export const getters = {
    nTimes() {
        return state.currentRecording.nTimes;
    },
    samplingFrequency() {
        return state.currentRecording.samplingFrequency;
    },
    channelAmount() {
        return state.currentRecording.channelNames.length;
    },
    durationString() {
        let duration =
            state.currentRecording.nTimes /
            state.currentRecording.samplingFrequency;
        const duration_minutes = Math.floor(duration / 60);
        const duration_seconds = duration % 60;

        if (duration_seconds !== 0 && duration_minutes !== 0) {
            return `${duration_minutes} min. ${duration_seconds} s`;
        } else if (duration_minutes === 0) {
            return `${duration_seconds} s`;
        } else {
            return `${duration_minutes} min.`;
        }
    }
};
