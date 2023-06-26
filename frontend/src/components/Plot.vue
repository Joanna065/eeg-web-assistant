<template>
    <v-card height="730">
        <v-skeleton-loader
            v-if="!layout"
            type="card-heading, image, image, card-avatar"
            height="730"
        ></v-skeleton-loader>

        <v-card v-else flat class="pa-5" height="730">
            <vue-plotly :data="traces" :layout="layout" :options="options" />
            <v-card-actions>
                <v-slider
                    v-model="recordStep"
                    step="1"
                    :loading="plotLoading"
                    ticks="always"
                    thumb-label
                    tick-size="4"
                    :disabled="plotLoading"
                    min="0"
                    :max="maxPlotFragmentNr"
                    @change="onSliderChange($event)"
                ></v-slider>
            </v-card-actions>
        </v-card>
    </v-card>
</template>

<script>
import VuePlotly from '@statnett/vue-plotly';
import { mapGetters, mapState } from 'vuex';

import PlotConfig from '@/configs/plot';
import store from '@/store';

export default {
    name: 'Plot',
    components: {
        VuePlotly
    },
    data: () => ({
        options: {},
        recordStep: 0,
        prevRecordStep: 0,
        plotLoading: false,
        traces: null,
        layout: null
    }),
    computed: {
        ...mapState({
            recording: state => state.analysis.currentRecording,
            plotData: state => state.plot.data,
            plotShapes: state => state.plot.shapes,
            plotChannels: state => state.plot.channels,
            plotSamplingFrequency: state => state.plot.samplingFrequency
        }),
        ...mapGetters('plot', [
            'maxPlotFragmentNr',
            'getShapesInFragment',
            'channelAmount'
        ])
    },
    methods: {
        onSliderChange(value) {
            if (this.prevRecordStep !== value) {
                this.prevRecordStep = value;
                this.fetchPlot();
            }
        },
        getLayout() {
            let step = 1 / this.channelAmount;
            let annotations = [];
            let yaxises = {};
            let shapes = [];

            for (let i = 0; i < this.channelAmount; i++) {
                const domain_start = i * step;
                const domain_stop = (i + 1) * step;

                let ann = {
                    x: -0.08,
                    y: 0,
                    xref: 'paper',
                    yref: `y${i + 1}`,
                    text: this.plotChannels[i].replace('EEG', ''),
                    showarrow: false
                };
                annotations.push(ann);

                yaxises[`yaxis${i + 1}`] = {
                    domain: [domain_start, domain_stop],
                    showticklabels: false,
                    zeroline: false,
                    showgrid: false
                };
            }

            for (let i = 0; i < this.getShapesInFragment.length; i++) {
                const start_x = parseInt(this.getShapesInFragment[i][0]);
                const end_x = parseInt(this.getShapesInFragment[i][1]);

                let shape = {
                    type: 'rect',
                    xref: 'x',
                    yref: 'paper',
                    x0: start_x,
                    y0: 0,
                    x1: end_x,
                    y1: 1,
                    fillcolor: 'blue',
                    opacity: 0.1,
                    line: {
                        width: 0
                    }
                };
                shapes.push(shape);
            }

            return {
                ...{
                    height: 650,
                    margin: {
                        l: 90,
                        r: 20,
                        b: 50,
                        t: 50,
                        pad: 5
                    },
                    title: {
                        text: 'EEG Channel data'
                    },
                    annotations: annotations,
                    showlegend: false,
                    xaxis: {
                        title: {
                            text: 'time (s)'
                        }
                    },
                    shapes: shapes
                },
                ...yaxises
            };
        },
        getTraces() {
            let traces = [];
            let xaxis = [];
            let startSecond =
                this.recordStep * PlotConfig.PLOT_FRAGMENT_SECONDS;

            for (let i = 0; i < this.plotData[0].length + 1; i++) {
                xaxis.push(i / this.plotSamplingFrequency + startSecond);
            }

            for (let i = 0; i < this.channelAmount; i++) {
                let subplot = {
                    x: xaxis,
                    y: this.plotData[i],
                    yaxis: `y${i + 1}`,
                    type: 'scattergl'
                };
                traces.push(subplot);
            }
            return traces;
        },
        redrawPlot() {
            this.traces = this.getTraces();
            this.layout = this.getLayout();
        },
        fetchPlot() {
            this.plotLoading = true;

            this.$store
                .dispatch('plot/fetchPlotFragment', {
                    id: this.recording.id,
                    sliderNr: this.recordStep
                })
                .then(() => {
                    this.$store.dispatch('plot/updatePlotFragmentNr', {
                        nr: this.recordStep
                    });

                    this.plotLoading = false;
                    this.redrawPlot();
                })
                .catch(error => {
                    this.plotLoading = false;
                    if (error.response) {
                        if (error.response.status === 400) {
                            this.$store.dispatch('analysis/showSnackbar', {
                                flag: true,
                                text: 'Plot fragment fetch failed',
                                color: 'error'
                            });
                        } else if (error.response.status === 401) {
                            store.dispatch('auth/logout');
                            this.$router.push('/sign-in');
                        } else if (error.response.status === 404) {
                            this.$router.push({
                                path: '/404',
                                params: { resource: 'analysis' }
                            });
                        } else if (error.response.status === 403) {
                            this.$router.push('/403-forbidden');
                        } else {
                            this.$store.dispatch('analysis/showSnackbar', {
                                flag: true,
                                text: 'Plot fragment fetch failed',
                                color: 'error'
                            });
                        }
                    }
                });
        }
    },
    async created() {
        await this.fetchPlot();

        this.unwatch = this.$store.watch(
            (state, getters) => getters['plot/getShapesInFragment'],
            (newValue, oldValue) => {
                if (!!newValue && newValue !== oldValue) {
                    this.redrawPlot();
                }
            },
            { deep: true }
        );
    },
    beforeDestroy() {
        this.unwatch();
    }
};
</script>

<style scoped></style>
