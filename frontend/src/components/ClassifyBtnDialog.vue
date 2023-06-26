<template>
    <v-dialog v-model="showDialog" max-width="410">
        <template v-slot:activator="{ on, attrs }">
            <v-btn
                rounded
                color="success"
                v-bind="attrs"
                v-on="on"
                @click="showDialog = true"
                :disabled="classifyBtnDisabled"
            >
                Classify
            </v-btn>
        </template>
        <v-card>
            <v-card-title>
                Available classifications
            </v-card-title>
            <v-card-text>
                <v-list>
                    <template
                        v-for="(classification,
                        index) in allClassificationTypes"
                    >
                        <v-list-item
                            :key="index"
                            :label="classification"
                            :value="classification"
                            readonly
                        >
                            <v-list-item-action>
                                <v-checkbox
                                    v-model="checkedClassifications"
                                    :label="classification.label"
                                    :value="classification.label"
                                    :key="index"
                                    :disabled="classification.disabled"
                                >
                                </v-checkbox>
                            </v-list-item-action>
                        </v-list-item>
                    </template>
                </v-list>

                <small
                    >*Remember that recording channel names must coincide with
                    those supported for classification. Their list can be found
                    in the "About" page.
                </small>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                    text
                    rounded
                    color="info"
                    class="pl-2 pr-2"
                    @click="handleCloseClassifyDialog"
                >
                    Close
                </v-btn>
                <v-btn
                    text
                    rounded
                    color="accent"
                    class="pl-2 pr-2"
                    @click="handleClassify"
                >
                    Save
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
import { mapGetters, mapState } from 'vuex';

export default {
    name: 'ClassifyBtnDialog',
    data: () => ({
        showDialog: false,
        checkedClassifications: []
    }),
    computed: {
        ...mapState({
            recording: state => state.analysis.currentRecording,
            allClassificationTypes: state =>
                state.classification.allClassificationTypes
        }),
        ...mapGetters('classification', [
            'availableClassificationLabels',
            'disabledClassifiedLabels'
        ]),
        classifyBtnDisabled() {
            const disabledArray = this.allClassificationTypes.map(
                val => val.disabled
            );
            return disabledArray.every(Boolean);
        }
    },
    methods: {
        handleClassify() {
            this.showDialog = false;
            let toClassify = this.checkedClassifications.filter(val =>
                this.availableClassificationLabels.includes(val)
            );

            for (let i = 0; i < toClassify.length; i++) {
                this.$store
                    .dispatch(
                        'classification/enqueueClassificationTaskOrGetResult',
                        {
                            id: this.recording.id,
                            classificationType: toClassify[i]
                        }
                    )
                    .then(() => {})
                    .catch(error => {
                        this.checkedClassifications = this.disabledClassifiedLabels;
                        if (error.response) {
                            if (error.response.status === 401) {
                                this.$router.push('/sign-in');
                            } else if (error.response.status === 403) {
                                this.$router.push('/403-forbidden');
                            } else if (error.response.status === 404) {
                                this.$router.push('/404');
                            } else {
                                this.$store.dispatch('analysis/showSnackbar', {
                                    flag: true,
                                    text: 'Classification task failed',
                                    color: 'error'
                                });
                            }
                        }
                    });
            }
        },
        handleCloseClassifyDialog() {
            this.showDialog = false;
            this.checkedClassifications = this.disabledClassifiedLabels;
        }
    },
    created() {
        this.checkedClassifications = this.disabledClassifiedLabels;
    }
};
</script>

<style scoped></style>
