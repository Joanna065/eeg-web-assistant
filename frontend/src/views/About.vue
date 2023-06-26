<template>
    <v-app>
        <v-container fluid style="background:#f5f5f5" class="pt-15 pb-15">
            <v-row align="center" justify="center">
                <v-col class="text-center" cols="6">
                    <h1 class="display-2 font-weight-thin mb-4 pb-2">
                        Automatize your EEG analysis <br />
                        and access it anywhere you want
                    </h1>
                    <v-divider />
                    <h3 class="subheading font-weight-thin pt-5">
                        For several years now, deep models have been applied in
                        many fields of medicine with promising results. They are
                        capable of capturing patterns invisible to the human
                        eye. To meet the needs of neurologists and researchers
                        related to brain science, we offer a web tool supported
                        by the latest developments in bioinformatics and machine
                        learning. Explore and analyse your recordings easily,
                        <br />
                        get classification results and access it later anytime
                        you want via Internet.
                    </h3>
                </v-col>
            </v-row>
        </v-container>

        <v-parallax src="@/assets/innovative_eye.jpg" class="img" />

        <v-container class="pt-10 pb-10">
            <v-row>
                <v-col cols="5" class="text-center">
                    <h4 class="display-1 font-weight-thin mb-2">
                        Analysis
                    </h4>
                    <v-divider />
                    <body class="font-weight-thin text-start mt-5">
                        Creating an analysis requires uploading the EDF file.
                        Due to current limitations it is possible to send
                        recording which duration does not exceed 30 minutes. The
                        tool will read all necessary data from the file and
                        display it on a board. In case your EEG recording has
                        anonymous or blank subject data, it is possible to edit
                        and save it regardless of the information contained in
                        EDF.
                    </body>

                    <body class="font-weight-thin text-start mt-5">
                        Visualizing EEG signals in the browser is not an easy
                        task. There are millions of data points in each channel
                        so in order to prevent slow plot loading, recording is
                        downsampled to 200 Hz and split to 64 seconds fragments
                        - use the slider to change currently displayed time
                        range. Plot is interactive, so feel free to zoom, pan
                        and export images.
                    </body>

                    <body class="font-weight-thin text-start mt-5">
                        The core of this tool is providing classifications. Each
                        16 seconds segment of recording gets a probability and
                        uncertainty measure. Obtained results are displayed in
                        the data table which rows can be easily sorted by the
                        desired minimum probability value.
                    </body>
                </v-col>
                <v-col cols="7">
                    <v-card>
                        <v-img src="@/assets/eeg_plot.png"></v-img>
                    </v-card>
                </v-col>
            </v-row>
        </v-container>
        <v-container class="pb-10 pt-10">
            <v-row>
                <v-col cols="5">
                    <v-card flat width="400">
                        <v-img src="@/assets/graph.svg"></v-img>
                    </v-card>
                </v-col>
                <v-col cols="7" class="text-center">
                    <h4 class="display-1 font-weight-thin mb-2">
                        Model
                    </h4>
                    <v-divider />
                    <body class="font-weight-thin text-start mt-5">
                        The key feature of deep learning (DL) models is the
                        ability to capture the spectral, temporal and spatial
                        characteristics of the raw EEG signal which is
                        significant in order to recognize abnormal or
                        artefactual data. This is also in line with the clinical
                        practise where all these three dimensions have to be
                        considered by experts in order to provide a correct
                        interpretation of the EEG recording. As a result, the
                        application of DL is gaining more popularity among many
                        different classification tasks - focusing on EEG data,
                        e. g. distinguishing between left and right hand
                        movement, detecting seizures, sleep stages or
                        artefactual time fragments.
                    </body>

                    <body class="font-weight-thin text-start mt-5">
                        The classification process in EEG Assistant is performed
                        by a model based on a graph structure with
                        <strong>attention mechanism</strong>. The architecture
                        is called InstaGAT and was introduced in the seminar
                        <a
                            href="https://www.researchgate.net/publication/339907287_An_Attention-based_Architecture_for_EEG_Classification"
                            >paper</a
                        >. The idea of attention is one of most recent and
                        influential in DL field. It allows to easily embed
                        external knowledge into the model and make if capable to
                        learn which portions of the data are relevant to the
                        solving task. This is expected to improve model
                        explainability and increase its accuracy.
                    </body>
                </v-col>
            </v-row>
        </v-container>

        <v-container fluid style="background:#f5f5f5" class="pt-10 pb-10">
            <v-container>
                <v-row align="center" justify="center">
                    <h4 class="display-1 font-weight-thin mb-5">
                        Preprocessing guideline
                    </h4>
                </v-row>
                <v-row align="center">
                    <v-col cols="5">
                        <body class="font-weight-thin text-start mt-5">
                            In order for the model to be able to classify
                            recording the proper preprocessing steps have to be
                            applied (presented on timeline). Dropping channels
                            is related to training process limitations. The
                            channels configuration which model is able to
                            classify is dictated by a common set of channel
                            names used in training data.
                        </body>

                        <body class="font-weight-thin text-start mt-5">
                            Eleven well-established frequency-domain and
                            time-domain features are computed from each EEG
                            frame of each individual EEG channel. The first ones
                            include spectral power of 4 well-known and
                            clinically relevant bands: alpha, beta, theta and
                            delta. Time-domain are as follows:
                        </body>
                        <ul class="font-weight-thin">
                            <li>mean</li>
                            <li>variance</li>
                            <li>skewness</li>
                            <li>kurtosis</li>
                            <li>zero-crossings</li>
                            <li>peak-to-peak distance</li>
                            <li>area under the curve</li>
                        </ul>
                        <body class="font-weight-thin text-start mt-5">
                            Additionally, the Spearman’s correlation coefficient
                            between each pair of EEG channels is computed thus
                            obtaining the correlation matrix for each timeframe.
                        </body>
                    </v-col>
                    <v-col cols="7">
                        <v-timeline>
                            <v-timeline-item fill-dot small right>
                                <v-card height="90" class="align-center pt-3">
                                    <v-card-title
                                        class="font-weight-thin justify-center"
                                    >
                                        Drop unsupported channels
                                    </v-card-title>
                                </v-card>
                            </v-timeline-item>

                            <v-timeline-item fill-dot small left>
                                <v-card height="90" class="align-center pt-3">
                                    <v-card-title
                                        class="font-weight-thin justify-center"
                                    >
                                        Split to 16 s segments
                                    </v-card-title>
                                </v-card>
                            </v-timeline-item>

                            <v-timeline-item fill-dot small rigth>
                                <v-card height="90" class="align-center pt-3">
                                    <v-card-title
                                        class="font-weight-thin justify-center"
                                    >
                                        Normalize min-max
                                    </v-card-title>
                                </v-card>
                            </v-timeline-item>

                            <v-timeline-item fill-dot small left>
                                <v-card height="90">
                                    <v-card-title
                                        class="font-weight-thin justify-center"
                                    >
                                        Divide each segment <br />
                                        to 8 timeframes
                                    </v-card-title>
                                </v-card>
                            </v-timeline-item>

                            <v-timeline-item fill-dot small right>
                                <v-card height="90" class="align-center pt-3">
                                    <v-card-title
                                        class="font-weight-thin justify-center"
                                    >
                                        Extract features
                                    </v-card-title>
                                </v-card>
                            </v-timeline-item>
                        </v-timeline>
                    </v-col>
                </v-row>
            </v-container>
        </v-container>
        <v-container class="pt-10 pb-10">
            <v-row align="center" justify="center">
                <h4 class="display-1 font-weight-thin mb-5">
                    Datasets
                </h4>
            </v-row>
            <v-row>
                <v-col class="text-center" cols="12">
                    <body class="font-weight-thin text-center mt-5 mb-5">
                        To train the model three different EEG datasets were
                        used. They are provided by the
                        <strong
                            >Temple University Hospital of Philadelphia</strong
                        >. <br />
                        All of them were recorded with sampling frequency 250 Hz
                        and 16 bit resolution. The selected montage was the
                        averaged reference (AR). <br />
                        Datasets are publicly available on the TUH
                        <a
                            href="https://www.isip.piconepress.com/projects/tuh_eeg/"
                            >website</a
                        >.
                    </body>
                </v-col>
            </v-row>
            <v-row align="center" justify="center">
                <v-col cols="4">
                    <v-card class="pa-5" height="400">
                        <v-card-text class="text-center">
                            <v-avatar color="accent" size="100">
                                <v-icon dark x-large>
                                    mdi-numeric-1
                                </v-icon>
                            </v-avatar>
                        </v-card-text>
                        <v-card-title
                            class="font-weight-medium mb-4 justify-center"
                        >
                            TUH EEG Abnormal
                        </v-card-title>
                        <v-card-subtitle class="text-center">
                            Focuses on distinguishing normal vs abnormal EEG
                            signals. More than 2 thousand samples, slightly
                            imbalanced.
                        </v-card-subtitle>
                    </v-card>
                </v-col>

                <v-col cols="4">
                    <v-card class="pa-5" height="400">
                        <v-card-text class="text-center">
                            <v-avatar color="accent" size="100">
                                <v-icon dark x-large>
                                    mdi-numeric-2
                                </v-icon>
                            </v-avatar>
                        </v-card-text>
                        <v-card-title
                            class="font-weight-medium mb-4 justify-center"
                        >
                            TUH EEG Artifact
                        </v-card-title>
                        <v-card-subtitle class="text-center">
                            Contains normal signal and those affected <br />
                            by 5 different types of artifacts (chewing, eye
                            movements, muscle artifacts, shivering). The
                            artifacts subclasses were generalized into one class
                            during training process. More than 3 thousand
                            samples.
                        </v-card-subtitle>
                    </v-card>
                </v-col>

                <v-col cols="4">
                    <v-card class="pa-5" height="400">
                        <v-card-text class="text-center">
                            <v-avatar color="accent" size="100">
                                <v-icon dark x-large>
                                    mdi-numeric-3
                                </v-icon>
                            </v-avatar>
                        </v-card-text>
                        <v-card-title
                            class="font-weight-medium mb-4 justify-center"
                        >
                            TUH EEG Seizure
                        </v-card-title>
                        <v-card-subtitle class="text-center">
                            Recordings with different seizure types. From this
                            dataset only two classes were chosen - focal
                            non-specific and general non-specific seizures. The
                            second one is considered the positive class here.
                            More than 5 thousand samples.
                        </v-card-subtitle>
                    </v-card>
                </v-col>
            </v-row>
        </v-container>
        <v-parallax dark src="@/assets/neuron.jpg">
            <v-row align="center" justify="center">
                <v-col cols="4">
                    <v-card dark flat class="img" color="rgb(0, 0, 0, 0.6)">
                        <v-card-text
                            class="display-1 text-center font-weight-thin mb-4"
                        >
                            <i
                                >"Please keep in mind that still nothing can
                                replace the experience of a doctor. The main
                                goal of this tool is to provide support in the
                                diagnostic decision and to convince people to
                                benefit from artificial intelligence
                                achievements."</i
                            >
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>
        </v-parallax>
    </v-app>
</template>

<script>
export default {
    name: 'About'
};
</script>

<style scoped>
.img {
    opacity: 0.9;
}
</style>
