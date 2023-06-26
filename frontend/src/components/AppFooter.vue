<template>
    <v-footer dark padless>
        <v-card class="flex" flat tile>
            <v-card-text class="primary py-2 white--text text-center">
                {{ new Date().getFullYear() }} — <strong>EEG Assistant</strong>
            </v-card-text>
        </v-card>
    </v-footer>
</template>

<script>
export default {
    name: 'AppFooter',
    data: () => ({
        links: [
            {
                label: 'Home',
                url: '/'
            },
            {
                label: 'About',
                url: '/about'
            },
            {
                label: 'Trial',
                url: '/trial'
            }
        ]
    })
};
</script>

<style scoped></style>
