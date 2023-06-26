<template>
    <v-app-bar app color="primary" dark>
        <div class="d-flex align-center ml-2 mr-4">
            <v-img
                class="mr-2"
                :src="require('@/assets/sygnet.svg')"
                :lazy-src="require('@/assets/sygnet.svg')"
                max-height="40"
                max-width="40"
                contain
            ></v-img>
            <router-link
                to="/"
                tag="v-toolbar-title"
                class="toolbar-title font-weight-thin"
            >
                EEG Assistant
            </router-link>
        </div>
        <v-spacer></v-spacer>

        <v-btn
            text
            rounded
            ripple
            class="ml-2 mr-2"
            to="/"
            active-class="active-class-btn-disabled"
        >
            Home
        </v-btn>

        <v-btn
            text
            rounded
            ripple
            class="ml-2 mr-2"
            to="/about"
            active-class="active-class-btn-disabled"
        >
            About
        </v-btn>

        <v-btn
            v-if="loggedIn"
            text
            rounded
            ripple
            to="/my-recordings"
            class="ml-2 mr-2"
            active-class="active-class-btn-disabled"
        >
            My recordings
        </v-btn>

        <v-btn
            v-if="!loggedIn"
            text
            rounded
            ripple
            class="ml-2 mr-2"
            to="/sign-in"
            active-class="active-class-btn-disabled"
            >Sign In
        </v-btn>
        <v-btn
            v-if="!loggedIn"
            text
            rounded
            ripple
            class="ml-2 mr-2"
            active-class="active-class-btn-disabled"
            to="/sign-up"
            backgroundColor
            :style="{ backgroundColor: '#5c6bc0' }"
        >
            Sign Up
        </v-btn>

        <v-btn
            v-if="loggedIn"
            rounded
            text
            to="/account-settings"
            active-class="active-class-btn-disabled"
        >
            @{{ loggedUsername }}
        </v-btn>

        <v-tooltip bottom v-if="loggedIn">
            <template v-slot:activator="{ on, attrs }">
                <v-btn
                    icon
                    aria-label="logout"
                    @click="logout"
                    v-bind="attrs"
                    v-on="on"
                    class="mr-1"
                >
                    <v-icon color="secondary">mdi-logout</v-icon>
                </v-btn>
            </template>
            <span>Logout</span>
        </v-tooltip>
    </v-app-bar>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
    name: 'AppNavigation',
    computed: {
        ...mapGetters('auth', ['loggedIn', 'loggedUsername'])
    },
    methods: {
        logout() {
            this.$store.dispatch('auth/logout');
            this.$router.push('/');
        }
    }
};
</script>

<style scoped>
.toolbar-title {
    color: white;
    text-decoration: inherit;
    font-size: 1.5em;
    cursor: pointer;
    font-weight: 450;
}

.active-class-btn-disabled::before {
    background-color: transparent;
}
</style>
