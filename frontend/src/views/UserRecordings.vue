<template>
    <v-container fluid class="pa-0">
        <v-img
            :src="require('@/assets/background_pattern_min.svg')"
            :lazy-src="require('@/assets/background_pattern_min.svg')"
            :height="imgHeight"
        >
            <v-sheet
                color="transparent"
                class="overflow-y-auto"
                :max-height="imgHeight"
            >
                <v-row no-gutters align="center" class="ma-4">
                    <v-col cols="12">
                        <v-card width="80em" class="mx-auto" flat>
                            <v-card-title>
                                <h2>My EEG recordings</h2>
                                <v-spacer />

                                <v-btn
                                    rounded
                                    color="success"
                                    @click="showNewAnalysisDialog = true"
                                >
                                    Add recording
                                </v-btn>
                                <v-dialog
                                    v-model="showNewAnalysisDialog"
                                    max-width="500"
                                >
                                    <v-card class="mx-auto pa-5">
                                        <v-card-title>
                                            Upload your EEG recording
                                        </v-card-title>
                                        <v-card-text>
                                            <v-form ref="newAnalysisForm">
                                                <v-text-field
                                                    prepend-icon="mdi-pen"
                                                    outlined
                                                    required
                                                    label="Recording name"
                                                    :rules="[
                                                        rules.required,
                                                        rules.fileNameMax
                                                    ]"
                                                    v-model.trim="
                                                        newAnalysisName
                                                    "
                                                    counter="30"
                                                    maxlength="30"
                                                />
                                                <v-file-input
                                                    v-model="uploadedFile"
                                                    outlined
                                                    show-size
                                                    chips
                                                    accept=".edf"
                                                    label="File input*"
                                                    :rules="[
                                                        rules.required,
                                                        rules.maxFileSize
                                                    ]"
                                                />
                                            </v-form>
                                            <small>
                                                * The recording (.edf) can last
                                                up to 30 minutes due to current
                                                limitations.
                                            </small>
                                        </v-card-text>
                                        <p
                                            v-if="errorFileMsg"
                                            class="text-center error--text"
                                        >
                                            {{ errorFileMsg }}
                                        </p>
                                        <v-progress-linear
                                            v-if="loadingFile"
                                            indeterminate
                                            color="accent"
                                        />
                                        <v-card-actions>
                                            <v-spacer></v-spacer>
                                            <v-btn
                                                text
                                                rounded
                                                color="info"
                                                class="pl-2 pr-2"
                                                @click="hideNewAnalysisDialog"
                                            >
                                                Close
                                            </v-btn>
                                            <v-btn
                                                text
                                                rounded
                                                color="secondary"
                                                class="pl-2 pr-2"
                                                @click="handleNewAnalysisUpload"
                                            >
                                                Add
                                            </v-btn>
                                        </v-card-actions>
                                    </v-card>
                                </v-dialog>
                            </v-card-title>

                            <v-card-actions>
                                <v-row align="baseline" justify="center">
                                    <v-col cols="6">
                                        <v-text-field
                                            id="search-recordings"
                                            outlined
                                            dense
                                            color="info"
                                            append-icon="mdi-magnify"
                                            v-model.trim="searchBy"
                                            placeholder="search"
                                            v-on:input="debounceSearchBy"
                                        ></v-text-field>
                                    </v-col>
                                    <v-col>
                                        <v-progress-circular
                                            indeterminate
                                            color="accent"
                                            size="21"
                                            width="2"
                                            v-if="filterLoading"
                                        ></v-progress-circular>
                                    </v-col>
                                    <v-spacer></v-spacer>
                                    <v-col cols="4">
                                        <v-select
                                            flat
                                            outlined
                                            v-model="sortBy"
                                            color="info"
                                            :items="sortByItems"
                                            dense
                                            solo
                                            @change="updateRecordings"
                                        ></v-select>
                                    </v-col>
                                </v-row>
                            </v-card-actions>

                            <template v-if="loadingList">
                                <v-divider></v-divider>
                                <v-container>
                                    <v-row align="center" justify="center">
                                        <v-col>
                                            <v-progress-circular
                                                :size="70"
                                                :width="7"
                                                indeterminate
                                                color="secondary"
                                                v-if="loadingList"
                                            ></v-progress-circular>
                                        </v-col>
                                    </v-row>
                                </v-container>
                            </template>

                            <v-card
                                v-if="!!recordingsList && recordingsList.length"
                            >
                                <v-list two-line>
                                    <template
                                        v-for="(item, index) in recordingsList"
                                    >
                                        <v-list-item
                                            :key="item._id"
                                            :to="`/analysis/${item._id}`"
                                        >
                                            <v-list-item-content>
                                                <v-list-item-title>
                                                    {{ item.name }}
                                                </v-list-item-title>

                                                <v-list-item-subtitle>
                                                    {{ item.subject_full_name }}
                                                </v-list-item-subtitle>
                                            </v-list-item-content>

                                            <v-spacer></v-spacer>

                                            <v-list-item-content>
                                                <v-list-item-subtitle>
                                                    created: {{ item.created }}
                                                </v-list-item-subtitle>
                                            </v-list-item-content>

                                            <v-list-item-action>
                                                <v-hover v-slot="{ hover }">
                                                    <v-btn
                                                        to="/my-recordings"
                                                        class="active-class-btn-disabled"
                                                        icon
                                                        @click="
                                                            handleRecordingDeletion(
                                                                item._id
                                                            )
                                                        "
                                                    >
                                                        <v-icon
                                                            :color="
                                                                hover
                                                                    ? 'error'
                                                                    : 'grey'
                                                            "
                                                            large
                                                        >
                                                            mdi-delete
                                                        </v-icon>
                                                    </v-btn>
                                                </v-hover>
                                            </v-list-item-action>
                                        </v-list-item>

                                        <v-divider
                                            v-if="
                                                !!recordingsList &&
                                                    index <
                                                        recordingsList.length -
                                                            1
                                            "
                                            :key="index"
                                        ></v-divider>
                                    </template>
                                </v-list>
                            </v-card>

                            <template
                                v-if="
                                    !fetchEmpty &&
                                        !!recordingsList &&
                                        recordingsList.length === 0
                                "
                            >
                                <v-divider></v-divider>
                                <v-sheet outlined>
                                    <v-card flat class="mx-auto" width="250">
                                        <v-row align="center" justify="center">
                                            <v-col class="shrink">
                                                <v-img
                                                    class="mt-2"
                                                    style="opacity: 0.6"
                                                    :src="
                                                        require('@/assets/no matches.svg')
                                                    "
                                                    :lazy-src="
                                                        require('@/assets/no matches.svg')
                                                    "
                                                    width="140"
                                                    height="140"
                                                    contain
                                                ></v-img>
                                            </v-col>
                                        </v-row>
                                        <v-card-title
                                            class="justify-center info--text mt-0 pt-0"
                                        >
                                            Whoops, no matches
                                        </v-card-title>
                                        <v-card-subtitle class="text-center">
                                            We couldn't find any search results.
                                            Try another filters.
                                        </v-card-subtitle>
                                    </v-card>
                                </v-sheet>
                            </template>

                            <template v-if="fetchEmpty">
                                <v-divider></v-divider>
                                <v-sheet outlined>
                                    <v-card flat class="mx-auto" width="250">
                                        <v-row align="center" justify="center">
                                            <v-col class="shrink">
                                                <v-img
                                                    class="mt-2"
                                                    style="opacity: 0.8"
                                                    :src="
                                                        require('@/assets/empty_list.svg')
                                                    "
                                                    :lazy-src="
                                                        require('@/assets/empty_list.svg')
                                                    "
                                                    width="140"
                                                    height="140"
                                                    contain
                                                ></v-img>
                                            </v-col>
                                        </v-row>
                                        <v-card-title
                                            class="justify-center info--text mt-0 pt-0"
                                        >
                                            Looks empty here
                                        </v-card-title>
                                        <v-card-subtitle class="text-center">
                                            Press the "new recording" button to
                                            start creating new recordings.
                                        </v-card-subtitle>
                                    </v-card>
                                </v-sheet>
                            </template>
                        </v-card>
                    </v-col>
                </v-row>
            </v-sheet>
        </v-img>
    </v-container>
</template>

<script>
import _ from 'lodash';
import { mapState } from 'vuex';

import Validation from '@/configs/validation';

export default {
    name: 'UserRecordings',
    metaInfo: {
        title: 'User Recordings View',
        titleTemplate: 'User Recordings',
        htmlAttrs: {
            lang: 'en',
            amp: true
        }
    },
    data: () => ({
        fetchEmpty: false,
        loadingList: false,
        filterLoading: false,

        searchBy: null,
        sortBy: 'newest',
        sortByItems: ['newest', 'oldest', 'subject A-Z', 'subject Z-A'],

        loadingFile: false,
        uploadedFile: undefined,
        showNewAnalysisDialog: false,
        newAnalysisName: '',
        errorFileMsg: '',
        rules: {
            required: value => !!value || 'This field is required',
            fileNameMax: v =>
                !v ||
                v.length <= Validation.MAX_CHARACTERS_RECORDING_NAME ||
                `Maximum length is ${Validation.MAX_CHARACTERS_RECORDING_NAME}`,
            maxFileSize: v =>
                !v | (v.size < 100000000) ||
                'File size should be less than 100 MB!'
        }
    }),
    computed: {
        ...mapState({
            recordingsList: state => state.recordingsList.recordingsList
        }),
        imgHeight() {
            return this.$vuetify.breakpoint.height - 110;
        }
    },
    methods: {
        debounceSearchBy: _.debounce(function() {
            this.filterLoading = true;
            this.$store
                .dispatch('recordingsList/getUserRecordings', {
                    filter_text: this.searchBy,
                    sort_by: this.sortBy
                })
                .then(() => {
                    this.filterLoading = false;
                })
                .catch(error => {
                    this.filterLoading = false;
                    if (error.response && error.response.status === 401) {
                        this.$store.dispatch('auth/logout');
                        this.$router.push('/sign-in');
                    }
                });
        }, 500),
        updateRecordings() {
            this.$store
                .dispatch('recordingsList/getUserRecordings', {
                    filter: this.searchBy,
                    sort_by: this.sortBy
                })
                .then(() => {
                    this.loadingList = false;
                })
                .catch(error => {
                    this.loadingList = false;
                    if (error.response && error.response.status === 401) {
                        this.$router.push('/sign-in');
                    }
                });
        },
        handleRecordingDeletion(recordingId) {
            this.$store
                .dispatch('recordingsList/deleteRecording', {
                    _id: recordingId
                })
                .then(() => {
                    if (this.recordingsList.length === 0) {
                        this.fetchEmpty = true;
                    }
                })
                .catch(error => {
                    if (error.response) {
                        if (error.response.status === 401) {
                            this.$router.push('/sign-in');
                        }
                        if (error.response.status === 403) {
                            this.$router.push('/403-forbidden');
                        }
                    }
                });
        },
        hideNewAnalysisDialog() {
            this.loadingFile = false;
            this.showNewAnalysisDialog = false;
            this.clearNewAnalysisDialog();
        },
        clearNewAnalysisDialog() {
            this.loadingFile = false;
            this.uploadedFile = undefined;
            this.newAnalysisName = '';
            this.$refs.newAnalysisForm.resetValidation();
        },
        handleNewAnalysisUpload() {
            if (this.$refs.newAnalysisForm.validate()) {
                if (this.uploadedFile && this.newAnalysisName) {
                    let formData = new FormData();
                    formData.append('new_file', this.uploadedFile);
                    this.loadingFile = true;

                    this.$store
                        .dispatch('uploadRecording/uploadFile', {
                            name: this.newAnalysisName,
                            new_file: formData
                        })
                        .then(response => {
                            this.loadingFile = false;
                            this.showNewAnalysisDialog = false;
                            this.clearNewAnalysisDialog();

                            const addedRecordingId = response.data;
                            this.$router.push(`/analysis/${addedRecordingId}`);
                        })
                        .catch(error => {
                            if (error.response) {
                                if (error.response.status === 400) {
                                    this.errorFileMsg = error.response.data.detail.toString();
                                } else if (error.response.status === 401) {
                                    this.$router.push('/sign-in');
                                }
                            }
                        });
                }
            }
        }
    },
    created() {
        this.loadingList = true;
        this.$store
            .dispatch('recordingsList/getUserRecordings', {
                filter: null,
                sort_by: null
            })
            .then(response => {
                this.loadingList = false;
                if (response.data.length === 0) {
                    this.fetchEmpty = true;
                }
            })
            .catch(() => {
                this.loadingList = false;
            });
    }
};
</script>

<style scoped>
.active-class-btn-disabled::before {
    background-color: transparent;
}
</style>
