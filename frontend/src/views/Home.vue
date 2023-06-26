<template>
    <v-app>
        <v-parallax dark src="@/assets/neuron_cell.jpg">
            <v-row align="center" justify="center">
                <v-col class="text-center" cols="12">
                    <h1 class="display-2 font-weight-thin mb-4">
                        EEG Assistant
                    </h1>
                    <h4 class="subheading">
                        Read and classify your EEG recordings using Deep
                        Learning models
                    </h4>
                </v-col>
            </v-row>
        </v-parallax>

        <v-container class="pt-10 pb-15">
            <v-row align="center" justify="center">
                <v-col class="text-center" cols="12">
                    <h1 class="display-1 font-weight mb-4">
                        Features
                    </h1>
                </v-col>
            </v-row>
            <v-row>
                <v-col>
                    <v-card class="pa-5" height="350">
                        <v-card-text class="text-center">
                            <v-avatar color="secondary" size="100">
                                <v-icon dark large>
                                    mdi-upload
                                </v-icon>
                            </v-avatar>
                        </v-card-text>
                        <v-card-title
                            class="font-weight-thin mb-4 justify-center"
                        >
                            EDF format support
                        </v-card-title>
                        <v-card-subtitle class="text-center">
                            Upload your EEG file using European Data Format from
                            which basic recording parameters, subject
                            information and raw data will be read and saved in
                            our storage.
                        </v-card-subtitle>
                    </v-card>
                </v-col>
                <v-col>
                    <v-card class="pa-5" height="350">
                        <v-card-text class="text-center">
                            <v-avatar color="secondary" size="100">
                                <v-icon dark large>
                                    mdi-playlist-edit
                                </v-icon>
                            </v-avatar>
                        </v-card-text>
                        <v-card-title
                            class="font-weight-thin mb-4 justify-center"
                        >
                            Classification reports
                        </v-card-title>
                        <v-card-subtitle class="text-center">
                            Generate classification reports for recording
                            fragments and see their class probability with
                            uncertainty in a neat data table format to browse
                            and sort easily.
                        </v-card-subtitle>
                    </v-card>
                </v-col>
                <v-col>
                    <v-card class="pa-5" height="350">
                        <v-card-text class="text-center">
                            <v-avatar color="secondary" size="100">
                                <v-icon dark large>
                                    mdi-chart-line
                                </v-icon>
                            </v-avatar>
                        </v-card-text>
                        <v-card-title
                            class="font-weight-thin mb-4 justify-center"
                        >
                            Visualisation
                        </v-card-title>
                        <v-card-subtitle class="text-center">
                            Explore EEG channel data on interactive plot, see
                            highlighted positive classified recording fragments
                            and download images.
                        </v-card-subtitle>
                    </v-card>
                </v-col>
            </v-row>
        </v-container>
        <v-container fluid style="background:#f5f5f5" class="pt-5 pb-15">
            <v-container>
                <v-row align="center" justify="center">
                    <v-col class="text-center" cols="12">
                        <h1 class="display-1 font-weight mb-4">
                            Available classifications
                        </h1>
                    </v-col>
                </v-row>
                <v-row align="center">
                    <v-col cols="7">
                        <v-card>
                            <v-img src="@/assets/eeg_record.jpg"></v-img>
                        </v-card>
                    </v-col>
                    <v-col cols="5">
                        <v-card flat>
                            <v-list style="background:#f5f5f5">
                                <v-list-item>
                                    <v-list-item-icon>
                                        <v-icon color="accent" x-large
                                            >mdi-check-bold</v-icon
                                        >
                                    </v-list-item-icon>
                                    <v-list-item-content>
                                        <h2 class="font-weight-thin">
                                            Abnormal
                                        </h2>
                                    </v-list-item-content>
                                </v-list-item>

                                <v-list-item>
                                    <v-list-item-icon>
                                        <v-icon color="accent" x-large
                                            >mdi-check-bold</v-icon
                                        >
                                    </v-list-item-icon>
                                    <v-list-item-content>
                                        <h2 class="font-weight-thin">
                                            Artifact
                                        </h2>
                                    </v-list-item-content>
                                </v-list-item>

                                <v-list-item>
                                    <v-list-item-icon>
                                        <v-icon color="accent" x-large
                                            >mdi-check-bold</v-icon
                                        >
                                    </v-list-item-icon>
                                    <v-list-item-content>
                                        <h2 class="font-weight-thin">
                                            Seizure
                                        </h2>
                                    </v-list-item-content>
                                </v-list-item>
                            </v-list>
                        </v-card>
                    </v-col>
                </v-row>
            </v-container>
        </v-container>

        <v-container class="pb-15 pt-10">
            <v-row align="center" justify="center">
                <v-col class="text-center" cols="12">
                    <h1 class="display-1 font-weight mb-4">
                        Applied AI
                    </h1>
                </v-col>
            </v-row>
            <v-row>
                <v-col>
                    <v-card
                        class="pa-5"
                        height="200"
                        outlined
                        style="border: 3px solid #5c6bc0"
                    >
                        <v-card-title
                            class="font-weight mb-4 justify-center secondary--text"
                        >
                            Latest trends
                        </v-card-title>
                        <v-card-subtitle class="text-center">
                            Graph model with attention used in this tool is
                            based on latest achievements of bioinformatics and
                            deep learning field.
                        </v-card-subtitle>
                    </v-card>
                </v-col>
                <v-col>
                    <v-card
                        class="pa-5"
                        height="200"
                        outlined
                        style="border: 3px solid #5c6bc0"
                    >
                        <v-card-title
                            class="font-weight justify-center secondary--text mb-4"
                        >
                            Probability measure
                        </v-card-title>
                        <v-card-subtitle class="text-center">
                            Each 16 s fragments of recording is assigned a
                            probability of positive class with uncertainty
                            achieved by Monte Carlo dropout technic.
                        </v-card-subtitle>
                    </v-card>
                </v-col>
                <v-col>
                    <v-card
                        outlined
                        class="pa-5"
                        height="200"
                        style="border: 3px solid #5c6bc0"
                    >
                        <v-card-title
                            class="font-weight mb-4 justify-center secondary--text"
                        >
                            Performance
                        </v-card-title>
                        <v-card-subtitle class="text-center">
                            Model was tuned extensively on open-source datasets
                            available from Temple University EEG Corpus in order
                            to achieve best metrics values and provide accurate
                            classification.
                        </v-card-subtitle>
                    </v-card>
                </v-col>
            </v-row>
        </v-container>
    </v-app>
</template>

<script>
export default {
    name: 'Home'
};
</script>

<style scoped>
.img {
    opacity: 0.9;
}

.cardColor {
    background: transparent;
}
</style>
