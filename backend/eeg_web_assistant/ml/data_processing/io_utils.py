import pickle
from pathlib import Path
from typing import Any, List, Tuple

import numpy as np

from eeg_web_assistant.services.logging import Logging

logger = Logging.get(__name__)


def save_pickle(filepath: Path, data: Any):
    with filepath.open(mode='wb') as file:
        logger.info(f'Saving data to file {filepath}')
        pickle.dump(data, file)


def open_pickle(filepath: Path) -> Any:
    with filepath.open(mode='rb') as file:
        logger.info(f'Loading data from file {filepath}')
        data = pickle.load(file)

        return data


def save_dataset(filepath: Path, data: np.ndarray, labels: np.ndarray,
                 labels_encoder: List[str], common_channels: List[str]):
    dataset = {'data': data,
               'labels': np.array(labels),
               'labels_encoder': labels_encoder,
               'common_channels': common_channels}

    save_pickle(filepath, dataset)


def open_dataset(filepath: Path) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
    dataset = open_pickle(filepath)

    data = dataset['data']
    labels = dataset['labels']
    labels_encoder = dataset['labels_encoder']
    common_channels = dataset['common_channels']

    logger.info("Dataset loaded with shape %s and labels {%s}", data.shape,
                ",".join(labels_encoder))

    return data, labels, labels_encoder, common_channels
