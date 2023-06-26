<template>
    <v-container fluid class="pa-0">
        <v-img
            :src="require('@/assets/background_pattern_min.svg')"
            :lazy-src="require('@/assets/background_pattern_min.svg')"
            :height="imgHeight"
        >
            <v-card width="400" class="mx-auto ma-10 pa-5">
                <v-card-text>
                    <v-form
                        id="signUpForm"
                        ref="signUpForm"
                        @submit.prevent="handleSignUp"
                    >
                        <v-text-field
                            outlined
                            maxlength="255"
                            label="First name"
                            v-model="firstName"
                            :rules="firstNameRules"
                            required
                        ></v-text-field>
                        <v-text-field
                            outlined
                            maxlength="255"
                            label="Last name"
                            v-model="lastName"
                            :rules="lastNameRules"
                            required
                        ></v-text-field>
                        <v-text-field
                            outlined
                            label="Email"
                            type="email"
                            v-model="email"
                            :rules="emailRules"
                            required
                            append-icon="mdi-email"
                        ></v-text-field>
                        <v-text-field
                            outlined
                            maxlength="50"
                            label="Username"
                            v-model="username"
                            counter="50"
                            :rules="usernameRules"
                            required
                        ></v-text-field>
                        <v-text-field
                            outlined
                            required
                            label="Password"
                            v-model="password"
                            maxlength="255"
                            :rules="passwordRules"
                            :type="showPassword ? 'text' : 'password'"
                            :append-icon="
                                showPassword ? 'mdi-eye' : 'mdi-eye-off'
                            "
                            @click:append="showPassword = !showPassword"
                        ></v-text-field>

                        <v-btn block type="submit" color="success">
                            Register
                        </v-btn>
                    </v-form>
                </v-card-text>

                <p v-if="errorDetailMsg" class="text-center error--text">
                    {{ errorDetailMsg }}
                </p>

                <v-card-text class="text-center">
                    By clicking Register, I agree that I have read and accepted
                    <a>EEG Assistant Terms & Conditions</a>
                </v-card-text>

                <v-divider></v-divider>

                <v-card-text class="text-center">
                    Already have an account?
                    <router-link to="/sign-in">Sign in</router-link>
                </v-card-text>
            </v-card>
        </v-img>
    </v-container>
</template>

<script>
import { mapState } from 'vuex';

import Validation from '@/configs/validation';

export default {
    name: 'SignUp',
    data: () => ({
        errorDetailMsg: '',
        showPassword: false,
        firstName: '',
        firstNameRules: [
            value => !!value || 'This field is required',
            value =>
                value.length <= Validation.MAX_CHARACTERS_FIRST_NAME ||
                `Maximum length is ${Validation.MAX_CHARACTERS_FIRST_NAME}.`
        ],
        lastName: '',
        lastNameRules: [
            value => !!value || 'This field is required',
            value =>
                value.length <= Validation.MAX_CHARACTERS_LAST_NAME ||
                `Maximum length is ${Validation.MAX_CHARACTERS_LAST_NAME}.`
        ],
        email: '',
        emailRules: [
            value => !!value || 'This field is required',
            value =>
                !value ||
                Validation.REGEX_EMAIL.test(value) ||
                'Please provide a valid email address'
        ],
        username: '',
        usernameRules: [
            value => !!value || 'This field is required',
            value =>
                value.length <= Validation.MAX_CHARACTERS_USERNAME ||
                `Maximum length is ${Validation.MAX_CHARACTERS_USERNAME}.`
        ],
        password: '',
        passwordRules: [
            value => !!value || 'This field is required',
            value =>
                value.length >= Validation.MIN_CHARACTERS_PASSWORD ||
                `Password must contain minimum ${Validation.MIN_CHARACTERS_PASSWORD} letters`,
            value =>
                value.length <= Validation.MAX_CHARACTERS_PASSWORD ||
                `Maximum length is ${Validation.MAX_CHARACTERS_PASSWORD}`
        ]
    }),
    computed: mapState({
        loggedIn: state => state.auth.loggedIn,
        imgHeight() {
            return this.$vuetify.breakpoint.height - 110;
        }
    }),
    created() {
        if (this.loggedIn) {
            this.$router.push('/my-recordings');
        }
    },
    methods: {
        handleSignUp() {
            if (this.$refs.signUpForm.validate()) {
                if (
                    this.firstName &&
                    this.lastName &&
                    this.email &&
                    this.username &&
                    this.password
                ) {
                    this.$store
                        .dispatch('userAccount/createUser', {
                            first_name: this.firstName,
                            last_name: this.lastName,
                            email: this.email,
                            username: this.username,
                            password: this.password
                        })
                        .then(() => {
                            this.$router.push('/sign-up-success');
                        })
                        .catch(error => {
                            if (
                                error.response &&
                                error.response.status === 400
                            ) {
                                this.errorDetailMsg = error.response.data.detail.toString();
                            }
                        });
                }
            }
        }
    }
};
</script>

<style scoped></style>
