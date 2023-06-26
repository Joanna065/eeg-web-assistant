<template>
    <v-container>
        <v-row>
            <v-col cols="4">
                <h3>Password:</h3>
            </v-col>
            <v-col cols="8">
                <v-card flat>
                    <v-card-text>
                        <v-form ref="passwordForm">
                            <v-text-field
                                dense
                                outlined
                                maxlength="255"
                                label="Current password"
                                v-model="currentPassword"
                                :rules="[rules.required]"
                                :type="
                                    showCurrentPassword ? 'text' : 'password'
                                "
                                :append-icon="
                                    showCurrentPassword
                                        ? 'mdi-eye'
                                        : 'mdi-eye-off'
                                "
                                @click:append="
                                    showCurrentPassword = !showCurrentPassword
                                "
                            ></v-text-field>
                            <v-text-field
                                dense
                                outlined
                                maxlength="255"
                                label="New password"
                                v-model="newPassword"
                                :rules="[
                                    rules.required,
                                    rules.passwordMin,
                                    rules.passwordMax
                                ]"
                                :type="showNewPassword ? 'text' : 'password'"
                                :append-icon="
                                    showNewPassword ? 'mdi-eye' : 'mdi-eye-off'
                                "
                                @click:append="
                                    showNewPassword = !showNewPassword
                                "
                            ></v-text-field>
                            <v-text-field
                                dense
                                outlined
                                label="Password confirmation"
                                v-model="passwordConfirmation"
                                :rules="[
                                    rules.required,
                                    passwordConfirmationRule
                                ]"
                                :type="
                                    showPasswordConfirmation
                                        ? 'text'
                                        : 'password'
                                "
                                :append-icon="
                                    showPasswordConfirmation
                                        ? 'mdi-eye'
                                        : 'mdi-eye-off'
                                "
                                @click:append="
                                    showPasswordConfirmation = !showPasswordConfirmation
                                "
                            ></v-text-field>
                        </v-form>
                    </v-card-text>
                    <p v-if="errorPasswordMsg" class="text-center error--text">
                        {{ errorPasswordMsg }}
                    </p>
                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn
                            @click="handleSavePassword"
                            rounded
                            color="accent"
                            class="pl-3 pr-3"
                        >
                            Save
                        </v-btn>
                        <v-btn
                            rounded
                            color="info"
                            @click="resetPasswordForm"
                            class="pl-3 pr-3"
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
    name: 'PasswordAccount',
    data: () => ({
        errorPasswordMsg: '',

        showCurrentPassword: false,
        showNewPassword: false,
        showPasswordConfirmation: false,

        currentPassword: '',
        newPassword: '',
        passwordConfirmation: '',

        rules: {
            required: value => !!value || 'This field is required',
            passwordMin: v =>
                !v ||
                v.length >= Validation.MIN_CHARACTERS_PASSWORD ||
                `Password must contain minimum ${Validation.MIN_CHARACTERS_PASSWORD} letters`,
            passwordMax: v =>
                !v ||
                v.length <= Validation.MAX_CHARACTERS_PASSWORD ||
                `Maximum length is ${Validation.MAX_CHARACTERS_PASSWORD}`
        }
    }),
    computed: {
        ...mapState({
            currentUser: state => state.userAccount.currentUser
        }),
        passwordConfirmationRule() {
            return (
                this.newPassword === this.passwordConfirmation ||
                'Password must match'
            );
        }
    },
    methods: {
        scrollToTop() {
            this.$vuetify.goTo(0, { duration: 300, easing: 'linear' });
        },
        handleSavePassword() {
            if (this.$refs.passwordForm.validate()) {
                if (
                    this.currentPassword &&
                    this.newPassword &&
                    this.newPassword === this.passwordConfirmation
                ) {
                    this.$store
                        .dispatch('userAccount/updateUserPassword', {
                            current_password: this.currentPassword,
                            new_password: this.newPassword
                        })
                        .then(() => {
                            this.$store.dispatch(
                                'userAccount/changeUpdateAlertValue',
                                true
                            );
                            this.scrollToTop();
                            this.errorPasswordMsg = '';
                            this.$refs.passwordForm.resetValidation();
                            this.$refs.passwordForm.reset();
                        })
                        .catch(error => {
                            if (error.response) {
                                this.$store.dispatch(
                                    'userAccount/changeUpdateAlertValue',
                                    false
                                );

                                if (error.response.status === 400) {
                                    this.errorPasswordMsg = error.response.data.detail.toString();
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
        resetPasswordForm() {
            this.$refs.passwordForm.resetValidation();
            this.$refs.passwordForm.reset();
        }
    }
};
</script>

<style scoped></style>
