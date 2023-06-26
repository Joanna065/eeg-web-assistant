<template>
    <v-container>
        <v-row>
            <v-col>
                <v-card width="400" class="mx-auto ma-5 pa-5">
                    <v-card-title class="justify-center">
                        <h2 class="success--text">Register successful!</h2>
                    </v-card-title>

                    <v-spacer></v-spacer>

                    <v-card-subtitle class="text-center">
                        Redirecting to login page...
                    </v-card-subtitle>

                    <v-card-actions class="justify-center">
                        <v-progress-circular
                            class="cen"
                            indeterminate
                            color="secondary"
                        ></v-progress-circular>
                    </v-card-actions>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
export default {
    name: 'SignUpSuccess',
    created() {
        setTimeout(() => this.$router.push({ path: '/sign-in' }), 3000);
    }
};
</script>

<style scoped></style>
