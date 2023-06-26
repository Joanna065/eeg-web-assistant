import warnings
from enum import Enum
from pathlib import Path

from pyeeglab import (AbsoluteArea, Bandpower, CommonChannelSet, Dataset, DynamicWindow,
                      ForkedPreprocessor, Kurtosis, LowestFrequency, Mean,
                      MinMaxCentralizedNormalization, PeakToPeak, Pipeline, Skewness,
                      SpearmanCorrelation, ToDataframe, ToMergedDataframes, ToNumpy,
                      TUHEEGAbnormalDataset, Variance, ZeroCrossing)

from eeg_web_assistant import settings
from eeg_web_assistant.ml.data_processing.io_utils import save_pickle

# Ignore MNE warnings
warnings.simplefilter(action='ignore')


class RawData(Enum):
    ABNORMAL_DIR = Path('/home/joanna/EEG_data/tuheeg_abnormal/')
    ARTIFACT_DIR = Path('/home/joanna/EEG_data/tuheeg_artifact/')
    SEIZURE_DIR = Path('/home/joanna/EEG_data/tuheeg_seizure/')


def build_data(dataset: Dataset):
    preprocessing = Pipeline([
        CommonChannelSet(),
        LowestFrequency(),
        ToDataframe(),
        MinMaxCentralizedNormalization(),
        DynamicWindow(8),
        ForkedPreprocessor(
            inputs=[
                SpearmanCorrelation(),
                Mean(),
                Variance(),
                Skewness(),
                Kurtosis(),
                ZeroCrossing(),
                AbsoluteArea(),
                PeakToPeak(),
                Bandpower(['Delta', 'Theta', 'Alpha', 'Beta'])
            ],
            output=ToMergedDataframes()
        ),
        ToNumpy()
    ])

    return dataset.set_pipeline(preprocessing).load()


if __name__ == '__main__':
    dataset = TUHEEGAbnormalDataset(str(RawData.ABNORMAL_DIR.value))
    dataset.set_minimum_event_duration(4)
    dataset.index()

    processed_dataset = build_data(dataset)

    common_channels = dataset.maximal_channels_subset
    processed_dataset['common_channels'] = common_channels

    print('--> Common channels:')
    print(common_channels)

    print('--> Data shape:')
    print(processed_dataset['data'].shape)

    save_pickle(settings.DatasetConfig.ABNORMAL_PROCESSED, processed_dataset)
