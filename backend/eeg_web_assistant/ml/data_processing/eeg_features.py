from typing import Tuple

import numpy as np
import pandas as pd
from scipy.integrate import simps
from scipy.stats import kurtosis, skew
from yasa import bandpower

from eeg_web_assistant.services.logging import Logging

logger = Logging.get(__name__)


class FeatureExtractor:
    def __init__(self, array: np.ndarray, sfreq: float,
                 bands: Tuple = ('Delta', 'Theta', 'Alpha', 'Beta')):
        self.array = array
        self.sfreq = sfreq
        self.bands = bands

    def extract(self) -> np.ndarray:
        assert self.array.ndim == 4

        logger.info("Calculating data features...")
        logger.debug("Shape of input data: %s", self.array.shape)

        extracted_features_per_segment = []
        for segment in self.array:
            extracted_features_per_frame = []

            for frame in segment:
                features = [self._spearman_correlation(frame),
                            self._mean(frame)[:, np.newaxis],
                            self._variance(frame)[:, np.newaxis],
                            self._skewness(frame)[:, np.newaxis],
                            self._kurtosis(frame)[:, np.newaxis],
                            self._zero_crossing_count(frame)[:, np.newaxis],
                            self._absolute_area_under_signal(frame)[:, np.newaxis],
                            self._peak_to_peak(frame)[:, np.newaxis],
                            self._bandpower(frame)]

                features = np.concatenate(features, axis=1)
                extracted_features_per_frame.append(features)

            extracted_features_per_segment.append(extracted_features_per_frame)

        all_features = np.array(extracted_features_per_segment)
        assert all_features.shape[:-1] == self.array.shape[:-1]

        logger.debug("Shape of extracted features array: %s", all_features.shape)

        return all_features

    def _bandpower(self, array: np.ndarray) -> np.ndarray:
        df = bandpower(array, sf=self.sfreq)
        df = df.loc[:, self.bands]
        return df.to_numpy()

    @staticmethod
    def _spearman_correlation(array: np.ndarray) -> np.ndarray:
        assert array.ndim == 2

        df = pd.DataFrame(data=array.T)
        return df.corr(method='spearman').to_numpy()

    @staticmethod
    def _mean(array: np.ndarray) -> np.ndarray:
        return np.mean(array, axis=1)

    @staticmethod
    def _variance(array: np.ndarray) -> np.ndarray:
        # unbiased estimator (ddof = 1)
        return np.var(array, axis=1, ddof=1)

    @staticmethod
    def _skewness(array: np.ndarray) -> np.ndarray:
        return skew(array, axis=1, bias=False, nan_policy='omit')

    @staticmethod
    def _kurtosis(array: np.ndarray) -> np.ndarray:
        return kurtosis(array, axis=1, bias=False, nan_policy='omit')

    @staticmethod
    def _zero_crossing_count(array: np.ndarray) -> np.ndarray:
        return np.count_nonzero(np.diff(np.sign(array)), axis=1)

    @staticmethod
    def _absolute_area_under_signal(array: np.ndarray) -> np.ndarray:
        return simps(np.abs(array), dx=1e-6, axis=1)

    @staticmethod
    def _peak_to_peak(array: np.ndarray) -> np.ndarray:
        return np.max(array, axis=1) - np.min(array, axis=1)
