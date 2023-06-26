<template>
    <v-container>
        <v-row>
            <v-col cols="4">
                <h3>Personal info:</h3>
            </v-col>
            <v-col cols="8">
                <v-card flat>
                    <v-card-text>
                        <v-form ref="personalInfoForm">
                            <v-text-field
                                dense
                                outlined
                                maxlength="255"
                                label="First name"
                                v-model.trim="firstName"
                                :rules="[rules.required, rules.firstNameMax]"
                            ></v-text-field>
                            <v-text-field
                                dense
                                outlined
                                maxlength="255"
                                label="Last name"
                                v-model.trim="lastName"
                                :rules="[rules.required, rules.lastNameMax]"
                            ></v-text-field>
                            <v-text-field
                                dense
                                outlined
                                label="Email"
                                type="email"
                                v-model="email"
                                :rules="[rules.email]"
                                append-icon="mdi-email"
                            ></v-text-field>
                        </v-form>
                    </v-card-text>
                    <p
                        v-if="errorPersonalInfoMsg"
                        class="text-center error--text"
                    >
                        {{ errorPersonalInfoMsg }}
                    </p>
                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn
                            @click="handleSavePersonalInfo"
                            rounded
                            class="pl-3 pr-3"
                            color="accent"
                        >
                            Save
                        </v-btn>
                        <v-btn
                            rounded
                            color="info"
                            class="pl-3 pr-3"
                            @click="resetPersonalInfoForm"
                        >
                            Reset
                        </v-btn>
                    </v-card-actions>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import { mapState } from 'vuex';

import Validation from '@/configs/validation';

export default {
    name: 'PersonalInfoAccount',
    data: () => ({
        errorPersonalInfoMsg: '',

        firstName: '',
        lastName: '',
        email: '',

        rules: {
            required: value => !!value || 'This field is required',
            firstNameMax: v =>
                !v ||
                v.length <= Validation.MAX_CHARACTERS_FIRST_NAME ||
                `Maximum length is ${Validation.MAX_CHARACTERS_FIRST_NAME}`,
            lastNameMax: v =>
                !v ||
                v.length <= Validation.MAX_CHARACTERS_LAST_NAME ||
                `Maximum length is ${Validation.MAX_CHARACTERS_LAST_NAME}`,
            email: v =>
                !v ||
                Validation.REGEX_EMAIL.test(v) ||
                'Please provide a valid email address'
        }
    }),

    computed: {
        ...mapState({
            currentUser: state => state.userAccount.currentUser
        })
    },
    methods: {
        scrollToTop() {
            this.$vuetify.goTo(0, { duration: 300, easing: 'linear' });
        },
        handleSavePersonalInfo() {
            if (this.$refs.personalInfoForm.validate()) {
                if (this.firstName && this.lastName && this.email) {
                    const changedEmail =
                        this.currentUser.email !== this.email
                            ? this.email
                            : null;
                    const changedFirstName =
                        this.currentUser.first_name !== this.firstName
                            ? this.firstName
                            : null;
                    const changedLastName =
                        this.currentUser.last_name !== this.lastName
                            ? this.lastName
                            : null;

                    this.$store
                        .dispatch('userAccount/updateUserPersonalInfo', {
                            first_name: changedFirstName,
                            last_name: changedLastName,
                            email: changedEmail
                        })
                        .then(() => {
                            this.$store.dispatch(
                                'userAccount/changeUpdateAlertValue',
                                true
                            );
                            this.scrollToTop();
                            this.errorPersonalInfoMsg = '';

                            this.firstName = this.currentUser.first_name;
                            this.lastName = this.currentUser.last_name;
                            this.email = this.currentUser.email;
                        })
                        .catch(error => {
                            if (error.response) {
                                this.$store.dispatch(
                                    'userAccount/changeUpdateAlertValue',
                                    false
                                );

                                if (error.response.status === 400) {
                                    this.errorPersonalInfoMsg = error.response.data.detail.toString();
                                } else if (error.response.status === 401) {
                                    this.$router.push('/sign-in');
                                } else if (error.response.status === 404) {
                                    this.$router.push('/404');
                                } else {
                                    this.$router.push('/network-issue');
                                }
                            }
                        });
                }
            }
        },
        resetPersonalInfoForm() {
            this.$refs.personalInfoForm.resetValidation();
            this.firstName = this.currentUser.first_name;
            this.lastName = this.currentUser.last_name;
            this.email = this.currentUser.email;
        }
    },
    created() {
        if (this.currentUser) {
            this.firstName = this.currentUser.first_name;
            this.lastName = this.currentUser.last_name;
            this.email = this.currentUser.email;
        } else {
            this.$store
                .dispatch('userAccount/getCurrentUser')
                .then(response => {
                    this.firstName = response.data.first_name;
                    this.lastName = response.data.last_name;
                    this.email = response.data.email;
                })
                .catch(error => {
                    if (error.response && error.response.status === 401) {
                        this.$router.push('/sign-in');
                    } else {
                        this.$router.push('/network-issue');
                    }
                });
        }
    }
};
</script>

<style scoped></style>
