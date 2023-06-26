import PlotConfig from '@/configs/plot';
import RecordingService from '@/services/recordings.service';

export const namespaced = true;

export const state = {
    currentFragmentNr: 0,
    channels: null,
    data: null,
    shapes: [],
    samplingFrequency: null
};

export const mutations = {
    SET_PLOT_FRAGMENT_NR(state, { nr }) {
        state.currentFragmentNr = nr;
    },
    SET_PLOT_DATA(state, { channels, data, samplingFrequency }) {
        state.channels = channels;
        state.data = data;
        state.samplingFrequency = samplingFrequency;
    },
    SET_PLOT_SHAPES(state, xArrayRanges) {
        state.shapes = xArrayRanges;
    },
    UNSET_PLOT_SHAPES(state) {
        state.shapes = [];
    },
    CLEAR_PLOT_DATA(state) {
        state.currentFragmentNr = 0;
        state.channels = null;
        state.data = null;
        state.shapes = {};
        state.samplingFrequency = null;
    }
};

export const actions = {
    fetchPlotFragment({ commit }, { id, sliderNr }) {
        return RecordingService.getEegPlotFragment(id, sliderNr).then(
            response => {
                commit('SET_PLOT_DATA', {
                    channels: response.data.ch_names,
                    data: response.data.data_array,
                    samplingFrequency: response.data.sfreq
                });
                return Promise.resolve(response);
            },
            error => {
                return Promise.reject(error);
            }
        );
    },
    updatePlotFragmentNr({ commit }, { nr }) {
        nr = parseInt(nr);

        if (nr >= 0) {
            commit('SET_PLOT_FRAGMENT_NR', { nr: nr });
        }
    },
    updatePlotShapes({ commit }, xArrayRanges) {
        commit('SET_PLOT_SHAPES', xArrayRanges);
    },
    resetPlotShapes({ commit }) {
        commit('UNSET_PLOT_SHAPES');
    },
    clearPlotData({ commit }) {
        commit('CLEAR_PLOT_DATA');
    }
};

export const getters = {
    maxPlotFragmentNr: (state, getters, rootState) => {
        let duration_seconds =
            rootState.analysis.currentRecording.nTimes /
            rootState.analysis.currentRecording.samplingFrequency;

        return Math.floor(duration_seconds / PlotConfig.PLOT_FRAGMENT_SECONDS);
    },
    getShapesInFragment() {
        if (Array.isArray(state.shapes) && state.shapes.length > 0) {
            let minX =
                state.currentFragmentNr * PlotConfig.PLOT_FRAGMENT_SECONDS;
            let maxX =
                (state.currentFragmentNr + 1) *
                PlotConfig.PLOT_FRAGMENT_SECONDS;

            return state.shapes.filter(val => val[0] >= minX && val[1] <= maxX);
        } else {
            return [];
        }
    },
    channelAmount() {
        if (!state.channels) {
            return 0;
        } else {
            return state.channels.length;
        }
    }
};
