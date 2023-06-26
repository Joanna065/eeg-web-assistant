import json
from unittest.mock import MagicMock

import numpy as np

from eeg_web_assistant.ml.data_processing.eeg_features import FeatureExtractor
from tests.unit import UnitTestCase

DATA_DIR = UnitTestCase.FIXTURE_DIR.joinpath('eeg_features')


class TestFeatureExtractor(UnitTestCase):

    def setUp(self) -> None:
        self.feature_extractor = FeatureExtractor(array=MagicMock(), sfreq=MagicMock(),
                                                  bands=MagicMock())

    def test_spearman_correlation(self):
        self._run_array_equal_subtests(test_name='spearman_corr',
                                       fun=self.feature_extractor._spearman_correlation)

    def test_mean(self):
        self._run_array_equal_subtests(test_name='mean', fun=self.feature_extractor._mean)

    def test_variance(self):

        self._run_array_equal_subtests(test_name='variance', fun=self.feature_extractor._variance)

    def test_skewness(self):
        self._run_array_equal_subtests(test_name='skewness', fun=self.feature_extractor._skewness)

    def test_kurtosis(self):
        self._run_array_equal_subtests(test_name='kurtosis', fun=self.feature_extractor._kurtosis)

    def test_zero_crossing_count(self):
        self._run_array_equal_subtests(test_name='zero_crossing',
                                       fun=self.feature_extractor._zero_crossing_count)

    def test_absolute_area_under_signal(self):
        self._run_array_equal_subtests(test_name='absolute_area_under_signal',
                                       fun=self.feature_extractor._absolute_area_under_signal)

    def test_peak_to_peak(self):
        self._run_array_equal_subtests(test_name='peak_to_peak',
                                       fun=self.feature_extractor._peak_to_peak)

    def test_bandpower(self):
        # GIVEN
        with DATA_DIR.joinpath('test_bandpower.json').open() as f:
            test_data = json.load(f)['bandpower']

        # WHEN
        for i, params in enumerate(test_data):
            input_array = np.array(params['input'])
            expected_array = np.array(params['expected_output'])

            with self.subTest(test_num=i):
                self.feature_extractor.sfreq = int(params['sfreq'])
                self.feature_extractor.bands = params['bands']
                actual = self.feature_extractor._bandpower(input_array)

                # THEN
                np.testing.assert_array_equal(actual, expected_array)

    def _run_array_equal_subtests(self, test_name: str, fun: callable):
        # GIVEN
        with DATA_DIR.joinpath(f'test_{test_name}.json').open() as f:
            test_data = json.load(f)[test_name]

        # WHEN
        for i, params in enumerate(test_data):
            input_array = np.array(params['input'])
            expected_array = np.array(params['expected_output'])

            with self.subTest(test_num=i):
                actual = fun(array=input_array)

                # THEN
                np.testing.assert_array_equal(actual, expected_array)
