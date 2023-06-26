import api from '@/services/api';

const resource = '/classification';

export default {
    enqueueClassification(recordingId, classificationType) {
        return api.patch(`${resource}/${recordingId}`, null, {
            params: { classification_type: classificationType }
        });
    },
    getClassificationResultFromTask(taskId) {
        return api.get(`${resource}/${taskId}`);
    },
    getClassificationReport(recordingId, classificationType, minProb, maxStd) {
        return api.get(`${resource}/${recordingId}/report`, {
            params: {
                classification_type: classificationType,
                min_prob: minProb,
                max_std: maxStd
            }
        });
    },
    deleteClassificationReport(recordingId, classificationType) {
        return api.delete(`${resource}/${recordingId}/report`, {
            params: { classification_type: classificationType }
        });
    }
};
