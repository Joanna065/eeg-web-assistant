<template>
    <v-container>
        <v-row>
            <v-col>
                <h1>Oops!</h1>
                <v-icon large color="primary darken-2">
                    mdi-emoticon-frown-outline
                </v-icon>
                <h3>The {{ resource }} you're looking for doesn't exist.</h3>
                <router-link to="/">Back to home page</router-link>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
export default {
    name: 'NotFound',
    props: {
        resource: {
            type: String,
            required: true
        }
    }
};
</script>

<style scoped></style>
