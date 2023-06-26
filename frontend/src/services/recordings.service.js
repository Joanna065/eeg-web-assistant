import api from '@/services/api';

const resource = '/recording';

let sortByDict = {
    newest: 'date.desc',
    oldest: 'date.asc',
    'subject A-Z': 'subject.asc',
    'subject Z-A': 'subject.desc'
};

export default {
    getAllRecordings(filterBy, sortBy) {
        const sortByParamMap = sortByDict[sortBy];

        return api.get(`${resource}/all`, {
            params: { filter_text: filterBy, sort_by: sortByParamMap }
        });
    },
    getRecordingById(id) {
        return api.get(`${resource}/${id}`);
    },
    deleteRecordingById(id) {
        return api.delete(`${resource}/${id}`);
    },
    createRecording(newRecording) {
        return api.post(`${resource}`, newRecording.new_file, {
            params: { name: newRecording.name }
        });
    },
    updateRecordingById(id, updateData) {
        return api.patch(`${resource}/${id}`, updateData);
    },
    updateRecordingSubjectById(id, updateSubject) {
        return api.patch(`${resource}/${id}/subject_info`, updateSubject);
    },
    getEegPlotFragment(id, nr) {
        return api.get(`${resource}/${id}/plot/${nr}`);
    }
};
