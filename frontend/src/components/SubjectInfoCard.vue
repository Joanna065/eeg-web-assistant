<template>
    <v-card flat outlined height="340">
        <v-card-title class="secondary white--text">
            <v-icon color="white" class="pr-2">
                mdi-account
            </v-icon>
            <span>Subject Info</span>
            <v-spacer />

            <v-dialog v-model="editSubjectInfo" max-width="400">
                <template v-slot:activator="{ on, attrs }">
                    <v-btn
                        icon
                        text
                        @click="editSubjectInfo = true"
                        v-bind="attrs"
                        v-on="on"
                    >
                        <v-icon color="accent">
                            mdi-pencil
                        </v-icon>
                    </v-btn>
                </template>
                <v-card class="mx-auto pa-5">
                    <v-card-title>
                        Edit subject data
                    </v-card-title>
                    <v-card-text>
                        <v-form ref="subjectEditForm">
                            <v-text-field
                                dense
                                outlined
                                required
                                label="First name*"
                                maxlength="255"
                                :rules="[rules.required, rules.subjectNamesMax]"
                                v-model.trim="subjectFirstName"
                            />
                            <v-text-field
                                dense
                                outlined
                                label="Middle name"
                                maxlength="255"
                                :rules="[rules.subjectNamesMax]"
                                v-model.trim="subjectMiddleName"
                            />
                            <v-text-field
                                dense
                                outlined
                                required
                                label="Last name*"
                                maxlength="255"
                                :rules="[rules.required, rules.subjectNamesMax]"
                                v-model.trim="subjectLastName"
                            />
                            <template>
                                <v-menu
                                    ref="birthdayMenu"
                                    v-model="birthdayMenu"
                                    :close-on-content-click="false"
                                    transition="scale-transition"
                                    offset-y
                                    min-width="250px"
                                >
                                    <template v-slot:activator="{ on, attrs }">
                                        <v-text-field
                                            outlined
                                            dense
                                            v-model="subjectBirthday"
                                            label="Birthday"
                                            append-icon="mdi-calendar"
                                            readonly
                                            v-bind="attrs"
                                            v-on="on"
                                        ></v-text-field>
                                    </template>
                                    <v-date-picker
                                        ref="birthdayPicker"
                                        v-model="subjectBirthday"
                                        :max="
                                            new Date()
                                                .toISOString()
                                                .substr(0, 10)
                                        "
                                        min="1900-01-01"
                                        @change="saveBirthday"
                                    ></v-date-picker>
                                </v-menu>
                            </template>
                            <v-select
                                outlined
                                dense
                                v-model="subjectSex"
                                :items="sexItems"
                                label="Sex"
                            ></v-select>
                            <v-select
                                outlined
                                dense
                                v-model="subjectHand"
                                :items="handItems"
                                label="Hand"
                            ></v-select>
                            <small>
                                * required
                            </small>
                        </v-form>
                    </v-card-text>
                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn
                            text
                            rounded
                            color="info"
                            class="pl-2 pr-2"
                            @click="handleCloseSubjectInfoUpdate"
                        >
                            Close
                        </v-btn>
                        <v-btn
                            text
                            rounded
                            color="accent"
                            class="pl-2 pr-2"
                            @click="handleSubjectInfoUpdate"
                        >
                            Save
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-dialog>
        </v-card-title>

        <v-divider></v-divider>

        <v-list dense>
            <v-list-item>
                <v-list-item-content>First name:</v-list-item-content>
                <v-list-item-content class="align-end">
                    {{
                        recording.subjectFirstName
                            ? recording.subjectFirstName
                            : '-'
                    }}
                </v-list-item-content>
            </v-list-item>

            <v-list-item>
                <v-list-item-content>
                    Middle name:
                </v-list-item-content>
                <v-list-item-content class="align-end">
                    {{
                        recording.subjectMiddleName
                            ? recording.subjectMiddleName
                            : '-'
                    }}
                </v-list-item-content>
            </v-list-item>

            <v-list-item>
                <v-list-item-content>Last name:</v-list-item-content>
                <v-list-item-content class="align-end">
                    {{
                        recording.subjectLastName
                            ? recording.subjectLastName
                            : '-'
                    }}
                </v-list-item-content>
            </v-list-item>

            <v-list-item>
                <v-list-item-content>Birthday:</v-list-item-content>
                <v-list-item-content class="align-end">
                    {{
                        recording.subjectBirthday
                            ? recording.subjectBirthday
                            : '-'
                    }}
                </v-list-item-content>
            </v-list-item>

            <v-list-item>
                <v-list-item-content>Sex:</v-list-item-content>
                <v-list-item-content class="align-end">
                    {{ recording.subjectSex ? recording.subjectSex : '-' }}
                </v-list-item-content>
            </v-list-item>

            <v-list-item>
                <v-list-item-content>Hand:</v-list-item-content>
                <v-list-item-content class="align-end">
                    {{ recording.subjectHand ? recording.subjectHand : '-' }}
                </v-list-item-content>
            </v-list-item>
        </v-list>
    </v-card>
</template>

<script>
import { mapGetters, mapState } from 'vuex';

import Validation from '@/configs/validation';

export default {
    name: 'SubjectInfoCard',
    data: () => ({
        editSubjectInfo: false,
        birthdayMenu: false,
        sexItems: ['unknown', 'male', 'female'],
        handItems: ['right', 'left', 'ambidextrous'],

        subjectFirstName: '',
        subjectLastName: '',
        subjectMiddleName: '',
        subjectBirthday: null,
        subjectSex: null,
        subjectHand: null,
        rules: {
            required: value => !!value || 'This field is required',
            subjectNamesMax: v =>
                !v ||
                v.length <= Validation.MAX_CHARACTERS_SUBJECT_NAMES ||
                `Maximum length is ${Validation.MAX_CHARACTERS_SUBJECT_NAMES}`
        }
    }),
    watch: {
        birthdayMenu(val) {
            val &&
                setTimeout(
                    () => (this.$refs.birthdayPicker.activePicker = 'YEAR')
                );
        }
    },
    computed: {
        ...mapState({
            recording: state => state.analysis.currentRecording
        }),
        ...mapGetters('analysis', ['channelAmount', 'durationString'])
    },
    methods: {
        saveBirthday(date) {
            this.$refs.birthdayMenu.save(date);
        },
        handleCloseSubjectInfoUpdate() {
            this.$refs.subjectEditForm.resetValidation();
            this.editSubjectInfo = false;
            this.setSubjectEditFields();
        },
        handleSubjectInfoUpdate() {
            if (this.$refs.subjectEditForm.validate()) {
                this.$store
                    .dispatch('analysis/updateRecordingSubject', {
                        id: this.recording.id,
                        updateSubject: {
                            first_name: this.subjectFirstName,
                            last_name: this.subjectLastName,
                            middle_name: this.subjectMiddleName,
                            birthday: this.subjectBirthday
                                ? this.subjectBirthday
                                : null,
                            sex: this.subjectSex ? this.subjectSex : null,
                            hand: this.subjectHand ? this.subjectHand : null
                        }
                    })
                    .then(() => {
                        this.$store.dispatch('analysis/showSnackbar', {
                            flag: true,
                            text: 'Update subject successful',
                            color: 'success'
                        });

                        this.editSubjectInfo = false;
                        this.$refs.subjectEditForm.resetValidation();
                        this.setSubjectEditFields();
                    })
                    .catch(error => {
                        this.$store.dispatch('analysis/showSnackbar', {
                            flag: true,
                            text: 'Update subject failed',
                            color: 'error'
                        });

                        this.editSubjectInfo = false;
                        this.$refs.subjectEditForm.resetValidation();
                        this.setSubjectEditFields();

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
        setSubjectEditFields() {
            this.subjectFirstName = this.recording.subjectFirstName;
            this.subjectLastName = this.recording.subjectLastName;
            this.subjectMiddleName = this.recording.subjectMiddleName;
            this.subjectBirthday = this.recording.subjectBirthday;
            this.subjectSex = this.recording.subjectSex;
            this.subjectHand = this.recording.subjectHand;
        }
    },
    created() {
        this.setSubjectEditFields();
    }
};
</script>

<style scoped></style>
