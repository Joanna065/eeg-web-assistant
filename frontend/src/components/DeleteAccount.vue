<template>
    <v-container>
        <v-row>
            <v-col cols="4">
                <h3>Delete account:</h3>
            </v-col>
            <v-col cols="8">
                <v-card flat>
                    <p class="ml-5">
                        Deletion of your account will clear all your recordings
                        history.
                    </p>
                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn
                            rounded
                            color="error"
                            class="pl-3 pr-3"
                            @click.stop="showDeleteDialog = true"
                        >
                            Delete
                        </v-btn>
                        <v-dialog v-model="showDeleteDialog" max-width="400">
                            <v-card>
                                <v-card-title>
                                    Confirm deletion of your account?
                                </v-card-title>
                                <v-card-text>
                                    This will result in erasing your account
                                    data and removing all your recordings
                                    information from our storage.
                                </v-card-text>
                                <v-card-actions>
                                    <v-spacer></v-spacer>
                                    <v-btn
                                        text
                                        color="info"
                                        @click="showDeleteDialog = false"
                                    >
                                        No
                                    </v-btn>
                                    <v-btn
                                        text
                                        color="error"
                                        @click="handleDeleteAccount"
                                    >
                                        Yes
                                    </v-btn>
                                </v-card-actions>
                            </v-card>
                        </v-dialog>
                    </v-card-actions>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
export default {
    name: 'DeleteAccount',
    data: () => ({
        showDeleteDialog: false
    }),
    methods: {
        handleDeleteAccount() {
            this.$store
                .dispatch('userAccount/deleteUserAccount')
                .then(() => {
                    this.$store.dispatch('auth/logout');
                    this.$router.push('/');
                })
                .catch(error => {
                    if (error.response) {
                        if (error.response.status === 401) {
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
};
</script>

<style scoped></style>
