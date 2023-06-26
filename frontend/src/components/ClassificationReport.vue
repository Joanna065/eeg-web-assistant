<template>
    <v-card flat>
        <v-card-title>
            <v-select
                clearable
                outlined
                dense
                suffix="%"
                v-model="minProb"
                label="Min probability"
                class="pr-5 shrink"
                menu-props="auto"
                :items="probSelectItems"
                @change="onMinProbChanged($event)"
            ></v-select>
            <v-select
                clearable
                outlined
                dense
                suffix="%"
                v-model="maxStd"
                label="Max uncertainty"
                class="pr-5 shrink"
                menu-props="auto"
                :items="stdSelectItems"
                @change="onMaxStdChanged($event)"
            ></v-select>
            <v-spacer />
            <v-btn
                v-if="!loadingResults"
                rounded
                color="error"
                @click="handleDeleteReport"
            >
                Delete
            </v-btn>
        </v-card-title>
        <v-data-table
            :key="`data-table-${this.classificationType}`"
            dense
            multi-sort
            :loading="loadingResults"
            loading-text="Loading results... Please wait"
            :headers="headers"
            :items="segments"
            :items-per-page="10"
            class="elevation-1"
        />
    </v-card>
</template>

<script>
import { mapGetters, mapState } from 'vuex';

export default {
    name: 'ClassificationReport',
    props: {
        classificationType: {
            type: String
        }
    },
    data: () => ({
        polling: null,
        loadingResults: false,
        minProb: undefined,
        maxStd: undefined,
        segments: []
    }),
    computed: {
        ...mapState({
            classificationResults: state =>
                state.classification.classificationResults,
            recording: state => state.analysis.currentRecording
        }),
        ...mapGetters('classification', ['classificationResultOrTaskId']),
        classification() {
            return this.classificationResultOrTaskId(this.classificationType);
        },
        headers() {
            return [
                {
                    text: 'Probability (%)',
                    align: 'start',
                    value: 'prob',
                    filter: value => {
                        if (!this.minProb) return true;
                        return parseFloat(value) >= parseFloat(this.minProb);
                    }
                },
                {
                    text: 'Uncertainty (%)',
                    value: 'std',
                    filter: value => {
                        if (!this.maxStd) return true;
                        return parseFloat(value) <= parseFloat(this.maxStd);
                    }
                },
                { text: 'Start time (s)', value: 'startTime' },
                { text: 'End time (s)', value: 'stopTime' }
            ];
        },
        probSelectItems() {
            return Array.from(Array(101).keys()).reverse();
        },
        stdSelectItems() {
            return Array.from(Array(101).keys()).map(val => val / 10);
        }
    },
    methods: {
        getTaskStatus() {
            if (this.classification?.taskId) {
                this.polling = setInterval(() => {
                    this.$store
                        .dispatch('classification/getResultsFromTask', {
                            taskId: this.classification.taskId,
                            classificationType: this.classificationType
                        })
                        .then(response => {
                            if (response.data.status === 'SUCCESS') {
                                this.loadingResults = false;
                                clearInterval(this.polling);
                                this.segments = this.classificationResults[
                                    this.classificationType
                                ];

                                this.$store.dispatch('analysis/showSnackbar', {
                                    flag: true,
                                    text: `Success classification for ${this.classificationType}`,
                                    color: 'success'
                                });
                            } else if (
                                response.data.status === 'FAILURE' ||
                                response.data.status === 'REVOKED'
                            ) {
                                clearInterval(this.polling);
                                this.loadingResults = false;

                                this.$store.dispatch('analysis/showSnackbar', {
                                    flag: true,
                                    text: `Classification task for ${this.classificationType} failed`,
                                    color: 'error'
                                });
                            }
                        })
                        .catch(error => {
                            if (
                                error.response &&
                                error.response.status === 401
                            ) {
                                this.$router.push('/sign-in');
                            }
                        });
                }, 2000);
            }
        },
        handleDeleteReport() {
            this.$store
                .dispatch('classification/deleteClassification', {
                    id: this.recording.id,
                    type: this.classificationType
                })
                .then(() => {
                    this.$store.dispatch('analysis/showSnackbar', {
                        flag: true,
                        text: `Successful delete for ${this.classificationType} classification report`,
                        color: 'success'
                    });
                    this.$destroy();
                })
                .catch(error => {
                    if (error.response) {
                        if (error.response.status === 401) {
                            this.$router.push('sign-in');
                        } else if (error.response.status === 403) {
                            this.$router.push('403-forbidden');
                        } else if (error.response.status === 404) {
                            this.$router.push('404');
                        } else {
                            this.$store.dispatch('analysis/showSnackbar', {
                                flag: true,
                                text: `Delete report of ${this.classificationType} type failed`,
                                color: 'error'
                            });
                        }
                    }
                });
        },
        onMinProbChanged(value) {
            let xRangeArray = this.getPlotShapesRange(value, this.maxStd);
            this.$store.dispatch('plot/updatePlotShapes', xRangeArray);
        },
        onMaxStdChanged(value) {
            let xRangeArray = this.getPlotShapesRange(this.minProb, value);
            this.$store.dispatch('plot/updatePlotShapes', xRangeArray);
        },
        getPlotShapesRange(minProb, maxStd) {
            if (!this.loadingResults) {
                let filteredResults = [];
                if (this.minProb && this.maxStd) {
                    filteredResults = this.classificationResults[
                        this.classificationType
                    ].filter(
                        value =>
                            value.prob >= minProb && value.std <= this.maxStd
                    );
                } else if (this.minProb) {
                    filteredResults = this.classificationResults[
                        this.classificationType
                    ].filter(value => value.prob >= minProb);
                } else if (this.maxStd) {
                    filteredResults = this.classificationResults[
                        this.classificationType
                    ].filter(value => value.std <= maxStd);
                }
                return filteredResults.map(val => [
                    val.startTime,
                    val.stopTime
                ]);
            }
        }
    },
    created() {
        if (this.classification?.taskId) {
            this.loadingResults = true;
            this.getTaskStatus();
        } else if (this.classification?.results) {
            this.segments = this.classification.results;
            clearInterval(this.polling);
        } else {
            clearInterval(this.polling);
        }
    },
    beforeDestroy() {
        clearInterval(this.polling);
    }
};
</script>

<style scoped></style>
