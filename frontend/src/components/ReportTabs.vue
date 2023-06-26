<template>
    <v-card flat v-if="disabledClassifiedLabels.length === 0">
        <v-divider></v-divider>
        <v-row align="center" justify="center">
            <v-col>
                <v-card flat class="mx-auto" width="500">
                    <v-card-title class="justify-center info--text">
                        No classifications
                    </v-card-title>
                    <v-card-subtitle class="text-center">
                        Click on "Classify" button to start creating
                        classification reports.
                    </v-card-subtitle>
                </v-card>
            </v-col>
        </v-row>
    </v-card>

    <v-card v-else>
        <v-tabs color="primary lighten-2" left v-model="activeTab">
            <v-tab
                v-for="item in disabledClassifiedLabels"
                :key="`tab-${item}`"
                @change="onTabChanged(item)"
            >
                {{ item }}
            </v-tab>

            <v-tab-item
                v-for="item in disabledClassifiedLabels"
                :key="`tab-item-${item}`"
            >
                <classification-report
                    v-bind:classificationType="item"
                ></classification-report>
            </v-tab-item>
        </v-tabs>
    </v-card>
</template>

<script>
import { mapGetters, mapState } from 'vuex';

import ClassificationReport from '@/components/ClassificationReport';

export default {
    name: 'Reports',
    data: () => ({
        activeTab: null
    }),
    components: {
        ClassificationReport
    },
    computed: {
        ...mapState({
            plotShapes: state => state.plot.shapes
        }),
        ...mapGetters('classification', ['disabledClassifiedLabels'])
    },
    methods: {
        onTabChanged() {
            if (this.plotShapes.length > 0) {
                this.$store.dispatch('plot/resetPlotShapes');
            }
        }
    }
};
</script>

<style scoped></style>
