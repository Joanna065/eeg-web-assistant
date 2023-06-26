from typing import List, Tuple

import numpy as np

from eeg_web_assistant import settings
from eeg_web_assistant.ml.data_processing.io_utils import open_dataset, save_dataset
from eeg_web_assistant.services.logging import Logging

logger = Logging.get(__name__)


def abnormal_to_2class(data: np.ndarray, labels: np.ndarray) \
        -> Tuple[np.ndarray, np.ndarray, List[str]]:
    logger.info("Changing ABNORMAL dataset to 2 classes labeling.")

    # relabel abnormal as 1 and normal as 0
    abnormal_indices = np.argwhere(labels == 0)
    normal_indices = np.argwhere(labels == 1)

    for index in abnormal_indices:
        labels[index] = 1

    for index in normal_indices:
        labels[index] = 0

    labels_encoder_changed = ['normal', 'abnormal']

    return data, labels, labels_encoder_changed


def artifact_to_2class(data: np.ndarray, labels: np.ndarray) \
        -> Tuple[np.ndarray, np.ndarray, List[str]]:
    logger.info("Changing ARTIFACT dataset to 2 classes labeling.")

    null_label_idx = labels_encoder.index('null')
    labels_changed = np.array([0 if label == null_label_idx else 1 for label in labels])
    labels_encoder_changed = ['null', 'artifact']

    logger.debug("Labels changed: %s", ",".join(labels_encoder_changed))

    assert list(np.unique(labels_changed)) == [0, 1], 'More than two classes!'
    assert len(labels_changed) == len(labels), 'Changed labels amount differ from the previous one.'

    return data, labels_changed, labels_encoder_changed


def seizure_to_2class(data: np.ndarray, labels: np.ndarray, labels_encoder: List[str]) \
        -> Tuple[np.ndarray, np.ndarray, List[str]]:
    logger.info("Changing SEIZURE dataset to 2 classes labeling.")

    shape = data.shape[1:]

    fnsz_idx = labels_encoder.index('fnsz')
    gnsz_idx = labels_encoder.index('gnsz')

    chosen_indices = np.argwhere(np.logical_or(labels == fnsz_idx, labels == gnsz_idx))

    data_changed = data[chosen_indices].reshape(-1, *shape)

    labels_changed = labels[chosen_indices].flatten()
    labels_changed = np.array([1 if label == gnsz_idx else 0 for label in labels_changed])

    labels_encoder_changed = ['fnsz', 'gnsz']

    return data_changed, labels_changed, labels_encoder_changed


if __name__ == '__main__':
    DATASET_PATH = settings.DatasetConfig.ABNORMAL_PROCESSED
    DATASET_NAME = DATASET_PATH.name

    data, labels, labels_encoder, common_channels = open_dataset(DATASET_PATH)
    data, labels, labels_encoder = abnormal_to_2class(data, labels)

    save_dataset(settings.DatasetConfig.ABNORMAL_TWO_CLASS, data, labels, labels_encoder,
                 common_channels)
