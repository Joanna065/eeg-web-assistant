import ClassificationSegment from '@/models/classification-segment';
import ClassificationService from '@/services/classification.service';

export const namespaced = true;

export const state = {
    classificationTaskQueue: {},
    classificationResults: {},
    allClassificationTypes: [
        {
            label: 'abnormal',
            disabled: false
        },
        {
            label: 'artifact',
            disabled: false
        },
        {
            label: 'seizure',
            disabled: false
        }
    ]
};

export const mutations = {
    ADD_CLASSIFICATION_TASK_ID(state, { type, taskId }) {
        state.classificationTaskQueue[type] = taskId;
        for (let i = 0; i < state.allClassificationTypes.length; i++) {
            if (state.allClassificationTypes[i].label === type) {
                state.allClassificationTypes[i].disabled = true;
            }
        }
    },
    REMOVE_CLASSIFICATION_TASK_ID(state, type) {
        delete state.classificationTaskQueue[type];

        let alreadyClassified = state.classificationResults?.[type]
            ? state.classificationResults[type]
            : null;

        if (!alreadyClassified) {
            for (let i = 0; i < state.allClassificationTypes.length; i++) {
                if (state.allClassificationTypes[i].label === type) {
                    state.allClassificationTypes[i].disabled = false;
                }
            }
        }
    },
    ADD_CLASSIFICATION_RESULT(state, { type, result }) {
        state.classificationResults[type] = result;
        for (let i = 0; i < state.allClassificationTypes.length; i++) {
            if (state.allClassificationTypes[i].label === type) {
                state.allClassificationTypes[i].disabled = true;
            }
        }
    },
    DELETE_CLASSIFICATION_RESULT(state, { type }) {
        delete state.classificationResults[type];
        delete state.classificationTaskQueue[type];

        for (let i = 0; i < state.allClassificationTypes.length; i++) {
            if (state.allClassificationTypes[i].label === type) {
                state.allClassificationTypes[i].disabled = false;
            }
        }
    },
    CLEAR_CLASSIFICATION_INFO(state) {
        state.classificationResults = {};
        state.classificationTaskQueue = {};
        for (let i = 0; i < state.allClassificationTypes.length; i++) {
            state.allClassificationTypes[i].disabled = false;
        }
    }
};

export const actions = {
    enqueueClassificationTaskOrGetResult(
        { commit },
        { id, classificationType }
    ) {
        return ClassificationService.enqueueClassification(
            id,
            classificationType
        ).then(
            response => {
                if (Array.isArray(response.data)) {
                    commit('ADD_CLASSIFICATION_RESULT', {
                        type: classificationType,
                        result: response.data.map(
                            value => new ClassificationSegment(value)
                        )
                    });
                } else {
                    commit('ADD_CLASSIFICATION_TASK_ID', {
                        type: classificationType,
                        taskId: response.data
                    });
                }
                return Promise.resolve(response);
            },
            error => {
                return Promise.reject(error);
            }
        );
    },
    getResultsFromTask({ commit }, { taskId, classificationType }) {
        return ClassificationService.getClassificationResultFromTask(
            taskId
        ).then(
            response => {
                if (response.data.status === 'SUCCESS') {
                    commit('ADD_CLASSIFICATION_RESULT', {
                        type: classificationType,
                        result: response.data.result.map(
                            value => new ClassificationSegment(value)
                        )
                    });

                    commit('REMOVE_CLASSIFICATION_TASK_ID', classificationType);
                } else if (
                    response.data.status === 'FAILURE' ||
                    response.data.status === 'REVOKED'
                ) {
                    commit('REMOVE_CLASSIFICATION_TASK_ID', classificationType);
                }
                return Promise.resolve(response);
            },
            error => {
                return Promise.reject(error);
            }
        );
    },
    deleteClassification({ commit }, { id, type }) {
        return ClassificationService.deleteClassificationReport(id, type).then(
            response => {
                commit('DELETE_CLASSIFICATION_RESULT', { type: type });
                return Promise.resolve(response);
            },
            error => {
                return Promise.reject(error);
            }
        );
    },
    addExistingClassification({ commit, state }, { recordingClassifications }) {
        for (let i = 0; i < state.allClassificationTypes.length; i++) {
            const classLabel = state.allClassificationTypes[i].label;

            if (recordingClassifications?.[classLabel]) {
                const classification = recordingClassifications[classLabel];

                commit('ADD_CLASSIFICATION_RESULT', {
                    type: classLabel,
                    result: classification.segments.map(
                        val => new ClassificationSegment(val)
                    )
                });
            }
        }
    },
    clearClassificationData({ commit }) {
        commit('CLEAR_CLASSIFICATION_INFO');
    }
};

export const getters = {
    availableClassificationLabels() {
        let available = [];
        for (let i = 0; i < state.allClassificationTypes.length; i++) {
            if (!state.allClassificationTypes[i].disabled) {
                available.push(state.allClassificationTypes[i].label);
            }
        }
        return available;
    },
    disabledClassifiedLabels() {
        let disabled = [];
        for (let i = 0; i < state.allClassificationTypes.length; i++) {
            if (state.allClassificationTypes[i].disabled) {
                disabled.push(state.allClassificationTypes[i].label);
            }
        }
        return disabled;
    },
    classificationResultOrTaskId: state => classificationType => {
        if (state.classificationResults?.[classificationType]) {
            return { results: state.classificationResults[classificationType] };
        } else if (state.classificationTaskQueue?.[classificationType]) {
            return {
                taskId: state.classificationTaskQueue[classificationType]
            };
        } else {
            return null;
        }
    }
};
