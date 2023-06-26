<template>
    <v-card flat outlined height="340">
        <v-card-title class="secondary white--text">
            <v-icon color="white" class="pr-2">
                mdi-head-dots-horizontal
            </v-icon>
            <span>Recording Info</span>
        </v-card-title>

        <v-divider></v-divider>

        <v-list dense>
            <v-list-item>
                <v-list-item-content>
                    Measure date:
                </v-list-item-content>
                <v-list-item-content class="align-end">
                    {{ recording.measureDate }}
                </v-list-item-content>
            </v-list-item>

            <v-list-item>
                <v-list-item-content>
                    Channel amount:
                </v-list-item-content>
                <v-list-item-content class="align-end">
                    {{ channelAmount }}
                </v-list-item-content>
            </v-list-item>
            <v-list-item>
                <v-list-item-content>
                    Sampling frequency:
                </v-list-item-content>
                <v-list-item-content class="align-end">
                    {{ recording.samplingFrequency }}
                    Hz
                </v-list-item-content>
            </v-list-item>
            <v-list-item>
                <v-list-item-content>
                    Highpass:
                </v-list-item-content>
                <v-list-item-content class="align-end">
                    {{ recordingHighpass }} Hz
                </v-list-item-content>
            </v-list-item>
            <v-list-item>
                <v-list-item-content>
                    Lowpass:
                </v-list-item-content>
                <v-list-item-content class="align-end">
                    {{ recordingLowpass }} Hz
                </v-list-item-content>
            </v-list-item>
            <v-list-item>
                <v-list-item-content>
                    Duration:
                </v-list-item-content>
                <v-list-item-content class="align-end">
                    {{ durationString }}
                </v-list-item-content>
            </v-list-item>
        </v-list>
    </v-card>
</template>

<script>
import { mapGetters, mapState } from 'vuex';

export default {
    name: 'RecordingInfoCard',
    data: () => ({}),
    computed: {
        ...mapState({
            recording: state => state.analysis.currentRecording
        }),
        ...mapGetters('analysis', ['channelAmount', 'durationString']),
        recordingHighpass() {
            return this.recording.highpass ? this.recording.highpass : null;
        },
        recordingLowpass() {
            return this.recording.lowpass ? this.recording.lowpass : null;
        }
    }
};
</script>

<style scoped></style>
