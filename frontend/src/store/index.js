import Vue from 'vue';
import Vuex from 'vuex';

import * as analysis from '@/store/modules/analysis.js';
import * as auth from '@/store/modules/auth.js';
import * as classification from '@/store/modules/classification.js';
import * as plot from '@/store/modules/plot.js';
import * as recordingsList from '@/store/modules/recordings-list.js';
import * as uploadRecording from '@/store/modules/upload-recording.js';
import * as userAccount from '@/store/modules/user-account.js';

Vue.use(Vuex);

export default new Vuex.Store({
    state: {},
    mutations: {},
    actions: {},
    modules: {
        auth,
        userAccount,
        recordingsList,
        uploadRecording,
        analysis,
        plot,
        classification
    }
});
