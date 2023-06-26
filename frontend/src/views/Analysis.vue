<template>
    <v-container fluid class="pl-10 pr-10">
        <v-snackbar
            v-model="showUpdateSnackbar"
            :timeout="snackbarTimeout"
            top
            :color="snackbarColor"
        >
            {{ snackbarText }}

            <template v-slot:action="{ attrs }">
                <v-btn icon text v-bind="attrs" @click="hideSnackbar">
                    <v-icon>
                        mdi-close
                    </v-icon>
                </v-btn>
            </template>
        </v-snackbar>

        <v-row>
            <v-col cols="12" md="5">
                <eeg-description></eeg-description>
            </v-col>

            <v-col cols="12" md="7">
                <plot></plot>
            </v-col>
        </v-row>
        <v-row>
            <v-col>
                <report-tabs></report-tabs>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import NProgress from 'nprogress';
import { mapState } from 'vuex';

import EegDescription from '@/components/EegDescription';
import Plot from '@/components/Plot';
import ReportTabs from '@/components/ReportTabs';
import store from '@/store/index';

export default {
    name: 'Analysis',
    props: ['id'],
    data: () => ({
        snackbarTimeout: 2000
    }),
    components: {
        EegDescription,
        Plot,
        ReportTabs
    },
    computed: mapState({
        recording: state => state.analysis.currentRecording,
        showUpdateSnackbar: state => state.analysis.showUpdateSnackbar,
        snackbarText: state => state.analysis.snackbarText,
        snackbarColor: state => state.analysis.snackbarColor
    }),
    watch: {
        showUpdateSnackbar() {
            setTimeout(() => {
                this.hideSnackbar();
            }, this.snackbarTimeout);
        }
    },
    methods: {
        hideSnackbar() {
            this.$store.dispatch('analysis/showSnackbar', {
                flag: false,
                text: null,
                color: 'info'
            });
        }
    },
    beforeRouteEnter(routeTo, routeFrom, next) {
        NProgress.start();

        store
            .dispatch('analysis/fetchRecording', routeTo.params.id)
            .then(() => {
                NProgress.done();
                next();
            })
            .catch(error => {
                NProgress.done();
                if (error.response) {
                    if (error.response.status === 401) {
                        store.dispatch('auth/logout');
                        next('/sign-in');
                    } else if (error.response.status === 404) {
                        next({
                            path: '/404',
                            params: { resource: 'analysis' }
                        });
                    } else if (error.response.status === 403) {
                        next('/403-forbidden');
                    } else {
                        next('/network-issues');
                    }
                }
            });
    },
    destroyed() {
        this.hideSnackbar();
        this.$store.dispatch('analysis/clearAnalysisData');
        this.$store.dispatch('plot/clearPlotData');
        this.$store.dispatch('classification/clearClassificationData');
    }
};
</script>

<style scoped></style>
