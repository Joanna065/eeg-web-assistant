<template>
    <v-container fluid class="pa-0">
        <v-img
            :src="require('@/assets/background_pattern_max.svg')"
            :lazy-src="require('@/assets/background_pattern_max.svg')"
            :height="imgHeight"
        >
            <v-card width="400" class="mx-auto ma-10 pa-5">
                <v-card-title class="justify-center">
                    <h1 class="display-1">Sign in</h1>
                </v-card-title>

                <v-card-text>
                    <v-form
                        id="signInForm"
                        ref="signInForm"
                        @submit.prevent="handleSignIn"
                    >
                        <v-text-field
                            outlined
                            required
                            name="username"
                            label="Username"
                            v-model="username"
                            maxlength="50"
                            :rules="usernameRules"
                            prepend-icon="mdi-account-circle"
                        />
                        <v-text-field
                            outlined
                            required
                            name="password"
                            label="Password"
                            v-model="password"
                            maxlength="255"
                            :rules="passwordRules"
                            :type="showPassword ? 'text' : 'password'"
                            prepend-icon="mdi-lock"
                            :append-icon="
                                showPassword ? 'mdi-eye' : 'mdi-eye-off'
                            "
                            @click:append="showPassword = !showPassword"
                        />

                        <v-btn block type="submit" color="accent">
                            Login
                        </v-btn>
                    </v-form>
                </v-card-text>

                <p v-if="errorDetailMsg" class="text-center error--text">
                    {{ errorDetailMsg }}
                </p>

                <v-card-text class="text-center">
                    Don't have an account?
                    <router-link to="/sign-up">Sign up</router-link>
                </v-card-text>
            </v-card>
        </v-img>
    </v-container>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'SignIn',
    data: () => ({
        errorDetailMsg: '',
        showPassword: false,
        username: '',
        usernameRules: [value => !!value || 'This field is required.'],
        password: '',
        passwordRules: [value => !!value || 'This field is required.']
    }),
    computed: {
        ...mapGetters('auth', ['loggedIn']),
        imgHeight() {
            return this.$vuetify.breakpoint.height - 110;
        }
    },
    created() {
        if (this.loggedIn) {
            this.$router.push('/my-recordings');
        }
    },
    methods: {
        handleSignIn() {
            if (this.$refs.signInForm.validate()) {
                if (this.username && this.password) {
                    let formData = new FormData(
                        document.getElementById('signInForm')
                    );

                    this.$store
                        .dispatch('auth/login', formData)
                        .then(() => {
                            this.$router.push('/my-recordings');
                        })
                        .catch(error => {
                            if (
                                error.response &&
                                error.response.status === 401
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
