<template>
    <v-container fluid class="pa-0">
        <v-img
            :src="require('@/assets/background_pattern_max.svg')"
            :lazy-src="require('@/assets/background_pattern_max.svg')"
            :height="imgHeight"
        >
            <v-sheet
                color="transparent"
                class="overflow-y-auto"
                :max-height="imgHeight"
            >
                <v-row no-gutters align="center" class="ma-4">
                    <v-col cols="12">
                        <v-alert
                            ref="successAlert"
                            :value="updateAlertValue"
                            border="left"
                            color="success"
                            outlined
                            text
                            width="60em"
                            class="mx-auto"
                            type="success"
                            dismissible
                            @input="closeAlert"
                        >
                            Account was updated successfully
                        </v-alert>

                        <v-card width="60em" class="mx-auto pl-10 pr-10">
                            <v-card-title v-if="!!currentUser">
                                Hi, {{ currentUser.first_name }} !
                            </v-card-title>

                            <v-divider v-if="!!currentUser"></v-divider>

                            <v-card-text>
                                <personal-info-account></personal-info-account>
                            </v-card-text>

                            <v-divider></v-divider>

                            <v-card-text>
                                <password-account></password-account>
                            </v-card-text>

                            <v-divider></v-divider>

                            <v-card-text>
                                <delete-account></delete-account>
                            </v-card-text>
                        </v-card>
                    </v-col>
                </v-row>
            </v-sheet>
        </v-img>
    </v-container>
</template>

<script>
import { mapState } from 'vuex';

import DeleteAccount from '@/components/DeleteAccount';
import PasswordAccount from '@/components/PasswordAccount';
import PersonalInfoAccount from '@/components/PersonalInfoAccount';

export default {
    name: 'AccountSettings',
    components: {
        DeleteAccount,
        PersonalInfoAccount,
        PasswordAccount
    },
    computed: {
        ...mapState({
            currentUser: state => state.userAccount.currentUser,
            updateAlertValue: state => state.userAccount.showUpdateSuccessAlert
        }),
        imgHeight() {
            return this.$vuetify.breakpoint.height - 110;
        }
    },
    methods: {
        closeAlert() {
            this.$store.dispatch('userAccount/changeUpdateAlertValue', false);
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
                });
        }
    }
};
</script>

<style scoped></style>
