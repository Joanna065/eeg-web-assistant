from typing import Tuple

import numpy as np
from sklearn.model_selection import train_test_split

from eeg_web_assistant.services.logging import Logging

logger = Logging.get(__name__)


def split_data(data: np.ndarray, labels: np.ndarray, test_size: float = 0.1, shuffle: bool = True) \
        -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    logger.info("Splitting data...")

    x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=test_size,
                                                        shuffle=shuffle, stratify=labels)

    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=test_size,
                                                      shuffle=shuffle, stratify=y_train)

    logger.debug(f'Split data - train: {len(y_train)}, val: {len(y_val)}, test: {len(y_test)}')

    return x_train, y_train, x_val, y_val, x_test, y_test
