<template>
    <v-card flat>
        <v-card-title>
            <h1>{{ recording.name }}</h1>

            <v-dialog v-model="editName" max-width="400">
                <template v-slot:activator="{ on, attrs }">
                    <v-btn
                        icon
                        text
                        color="accent"
                        class="ml-5"
                        v-bind="attrs"
                        v-on="on"
                        @click="editName = true"
                    >
                        <v-icon>mdi-pencil</v-icon>
                    </v-btn>
                </template>
                <v-card>
                    <v-card-title>
                        Edit recording name
                    </v-card-title>
                    <v-card-text>
                        <v-form ref="editNameForm">
                            <v-text-field
                                outlined
                                label="Recording name"
                                counter="30"
                                maxlength="30"
                                :rules="[rules.required, rules.nameMax]"
                                v-model="recordingName"
                            >
                            </v-text-field>
                        </v-form>
                    </v-card-text>
                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn
                            text
                            rounded
                            color="info"
                            class="pl-2 pr-2"
                            @click="handleCloseNameUpdate"
                        >
                            Close
                        </v-btn>
                        <v-btn
                            text
                            rounded
                            color="accent"
                            class="pl-2 pr-2"
                            @click="handleNameUpdate"
                        >
                            Save
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-dialog>
            <v-spacer />
            <classify-btn-dialog />
        </v-card-title>

        <v-card-subtitle> created: {{ recording.created }} </v-card-subtitle>

        <v-card-text>
            <v-row>
                <v-col cols="6">
                    <recording-info-card></recording-info-card>
                </v-col>
                <v-col cols="6">
                    <subject-info-card></subject-info-card>
                </v-col>
            </v-row>
            <v-row>
                <v-col cols="12">
                    <v-card flat outlined height="260">
                        <v-card-title class="secondary white--text">
                            <v-icon class="pr-2" color="white">
                                mdi-note
                            </v-icon>
                            <span>Notes</span>
                            <v-spacer />
                            <v-btn
                                v-if="readonlyNotes"
                                icon
                                text
                                @click="readonlyNotes = false"
                            >
                                <v-icon color="accent">mdi-pencil </v-icon>
                            </v-btn>

                            <v-btn
                                v-if="!readonlyNotes"
                                icon
                                text
                                color="error"
                                @click="handleCloseNotesUpdate"
                            >
                                <v-icon size="30">
                                    mdi-close
                                </v-icon>
                            </v-btn>
                            <v-btn
                                v-if="!readonlyNotes"
                                icon
                                text
                                color="success"
                                @click="handleNotesUpdate"
                            >
                                <v-icon size="30">
                                    mdi-check
                                </v-icon>
                            </v-btn>
                        </v-card-title>
                        <v-card-text>
                            <v-textarea
                                rows="5"
                                :counter="readonlyNotes ? null : 500"
                                maxlength="500"
                                :readonly="readonlyNotes"
                                :auto-grow="false"
                                :no-resize="true"
                                placeholder="Write here your notes."
                                v-model="notes"
                                :rules="[rules.notesMax]"
                            >
                            </v-textarea>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>
        </v-card-text>
    </v-card>
</template>

<script>
import { mapGetters, mapState } from 'vuex';

import ClassifyBtnDialog from '@/components/ClassifyBtnDialog';
import RecordingInfoCard from '@/components/RecordingInfoCard';
import SubjectInfoCard from '@/components/SubjectInfoCard';
import Validation from '@/configs/validation';

export default {
    name: 'EegRecordInfo',
    components: {
        RecordingInfoCard,
        SubjectInfoCard,
        ClassifyBtnDialog
    },
    data: () => ({
        snackbarTimeout: 2000,

        readonlyNotes: true,
        editName: false,
        notes: '',
        recordingName: '',

        rules: {
            required: value => !!value || 'This field is required',
            notesMax: v =>
                !v ||
                v.length <= Validation.MAX_CHARACTERS_RECORDING_NOTES ||
                `Maximum length is ${Validation.MAX_CHARACTERS_RECORDING_NOTES}`,
            nameMax: v =>
                !v ||
                v.length <= Validation.MAX_CHARACTERS_RECORDING_NAME ||
                `Maximum length is ${Validation.MAX_CHARACTERS_RECORDING_NAME}`
        }
    }),
    computed: {
        ...mapState({
            recording: state => state.analysis.currentRecording
        }),
        ...mapGetters('analysis', ['channelAmount', 'durationString'])
    },
    created() {
        this.notes = this.recording?.notes ? this.recording.notes : '';
        this.recordingName = this.recording.name;
    },
    methods: {
        handleNotesUpdate() {
            this.readonlyNotes = true;

            this.$store
                .dispatch('analysis/updateRecording', {
                    id: this.recording.id,
                    updateData: { notes: this.notes }
                })
                .then(() => {
                    this.notes = this.recording.notes;

                    this.$store.dispatch('analysis/showSnackbar', {
                        flag: true,
                        text: 'Update notes successful',
                        color: 'success'
                    });
                })
                .catch(error => {
                    this.notes = this.recording.notes;

                    this.$store.dispatch('analysis/showSnackbar', {
                        flag: true,
                        text: 'Update notes failed',
                        color: 'error'
                    });

                    if (error.response) {
                        if (error.response.status === 401) {
                            this.$router.push('/sign-in');
                        } else if (error.response.status === 403) {
                            this.$router.push('/403-forbidden');
                        } else if (error.response.status === 404) {
                            this.$router.push('/403-forbidden');
                        }
                    }
                });
        },
        handleNameUpdate() {
            if (this.$refs.editNameForm.validate()) {
                this.editName = false;
                const changedName =
                    this.recording.name !== this.recordingName
                        ? this.recordingName
                        : null;

                this.$store
                    .dispatch('analysis/updateRecording', {
                        id: this.recording.id,
                        updateData: { name: changedName }
                    })
                    .then(() => {
                        this.recordingName = this.recording.name;

                        this.$store.dispatch('analysis/showSnackbar', {
                            flag: true,
                            text: 'Update name successful',
                            color: 'success'
                        });
                    })
                    .catch(error => {
                        this.recordingName = this.recording.name;

                        this.$store.dispatch('analysis/showSnackbar', {
                            flag: true,
                            text: 'Update name failed',
                            color: 'error'
                        });

                        if (error.response) {
                            if (error.response.status === 401) {
                                this.$router.push('/sign-in');
                            } else if (error.response.status === 403) {
                                this.$router.push('/403-forbidden');
                            } else if (error.response.status === 404) {
                                this.$router.push('/403-forbidden');
                            }
                        }
                    });
            }
        },
        handleCloseNotesUpdate() {
            this.notes = this.recording.notes;
            this.readonlyNotes = true;
        },
        handleCloseNameUpdate() {
            this.recordingName = this.recording.name;
            this.$refs.editNameForm.resetValidation();
            this.editName = false;
        }
    }
};
</script>

<style scoped></style>
