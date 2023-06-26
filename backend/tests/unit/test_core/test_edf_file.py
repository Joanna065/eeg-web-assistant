import json
from unittest.mock import MagicMock, patch

import numpy as np

from eeg_web_assistant.core.classification_types import ClassificationType
from eeg_web_assistant.core.edf_file import EdfFile, EdfProcessor
from tests.unit import UnitTestCase

DATA_DIR = UnitTestCase.FIXTURE_DIR.joinpath('edf_processing')


class EdfFileTestConfig:
    EDF_FILE_EXCLUDE = DATA_DIR.joinpath('edf_file_config_with_exclude.json')


class EdfProcessorCorrectTestConfig:
    EDF_CHANNELS_SETUP = DATA_DIR.joinpath('edf_file_classify_channels_correct.json')
    SEGMENT_LEN_SECONDS = 16
    TIMEFRAMES_AMOUNT = 8


class EdfProcessorErrorTestConfig:
    EDF_CHANNELS_SETUP = DATA_DIR.joinpath('edf_file_classify_channels_correct.json')
    SEGMENT_LEN_SECONDS = 16
    TIMEFRAMES_AMOUNT = 7


class TestEdfFile(UnitTestCase):

    @patch('eeg_web_assistant.core.edf_file.EdfFile._load', MagicMock())
    def setUp(self) -> None:
        self.edf_file = EdfFile(path=DATA_DIR.joinpath('edf_file_seizure_all_channels.edf'),
                                config=EdfFileTestConfig())

    @patch('eeg_web_assistant.core.edf_file.mne.io', MagicMock())
    def test_load__check_load_config_call(self):
        # GIVEN
        self.edf_file._load_config = MagicMock()

        # WHEN
        self.edf_file._load()

        # THEN
        self.edf_file._load_config.assert_called_once()

    @patch('eeg_web_assistant.core.edf_file.mne.io')
    def test_load__check_mne_read_raw_call(self, mne_io):
        # GIVEN
        self.edf_file._load_config = MagicMock()

        # WHEN
        self.edf_file._load()

        # THEN
        mne_io.read_raw_edf.assert_called_once()

    @patch('eeg_web_assistant.core.edf_file.mne.io', MagicMock())
    def test_load__check_drop_channels_call_if_exclude_not_none(self):
        # GIVEN
        self.edf_file._load_config = MagicMock()
        self.edf_file.exclude_channels = ['BURSTS']
        self.edf_file.drop_channels = MagicMock(drop_names=self.edf_file.exclude_channels)

        # WHEN
        self.edf_file._load()

        # THEN
        self.edf_file.drop_channels.assert_called_once()

    @patch('eeg_web_assistant.core.edf_file.mne.io', MagicMock())
    def test_load__check_drop_channels_call_if_exclude_none(self):
        # GIVEN
        self.edf_file._load_config = MagicMock()
        self.edf_file.exclude_channels = None
        self.edf_file.drop_channels = MagicMock(drop_names=self.edf_file.exclude_channels)

        # WHEN
        self.edf_file._load()

        # THEN
        self.edf_file.drop_channels.assert_not_called()

    def test_load_config__when_exclude_key_exists_in_config(self):
        # GIVEN
        with self.edf_file.config.EDF_FILE_EXCLUDE.open(mode='r') as f:
            edf_file_setup = json.load(f)

        expected_excluded_channels = edf_file_setup['exclude']

        # WHEN
        self.edf_file._load_config()

        # THEN
        self.assertEqual(self.edf_file.exclude_channels, expected_excluded_channels)

    def test_load_config__when_exclude_key_non_exists_in_config(self):
        # GIVEN
        self.edf_file.config.EDF_FILE_EXCLUDE = DATA_DIR.joinpath('edf_file_config_wo_exclude.json')

        # WHEN
        self.edf_file._load_config()

        # THEN
        self.assertEqual(self.edf_file.exclude_channels, None)

    def test_change_duration(self):
        # GIVEN
        self.edf_file._load()

        new_duration = self.edf_file.duration - 10
        # WHEN
        self.edf_file.change_duration(new_duration=new_duration)

        # THEN
        self.assertEqual(new_duration, self.edf_file.duration)


class TestEdfProcessor(UnitTestCase):
    def setUp(self) -> None:
        edf_record = MagicMock()
        edf_record.config = EdfFileTestConfig()
        self.edf_processor = EdfProcessor(edf_record=edf_record, classification_type=MagicMock())

    def test_load_config__correct_config(self):
        # GIVEN
        with EdfProcessorCorrectTestConfig().EDF_CHANNELS_SETUP.open(mode='r') as f:
            edf_chan_setup = json.load(f)

        eeg_class = ClassificationType.SEIZURE
        self.edf_processor.classification_type = eeg_class

        frames_num = EdfProcessorCorrectTestConfig.TIMEFRAMES_AMOUNT
        segment_len = EdfProcessorCorrectTestConfig.SEGMENT_LEN_SECONDS

        expected_frame_len = int(segment_len / frames_num)
        expected_channels = edf_chan_setup[eeg_class.value]

        # WHEN
        self.edf_processor.config = EdfProcessorCorrectTestConfig()
        self.edf_processor._load_config()

        # THEN
        self.assertEqual(frames_num, self.edf_processor.frames_amount)
        self.assertEqual(segment_len, self.edf_processor.segment_len)
        self.assertEqual(expected_frame_len, self.edf_processor.frame_len)
        self.assertSetEqual(set(expected_channels), set(self.edf_processor.common_channels))

    def test_load_config__raise_error(self):
        # GIVEN
        self.edf_processor.frames_num = EdfProcessorErrorTestConfig.TIMEFRAMES_AMOUNT
        self.edf_processor.segment_len = EdfProcessorErrorTestConfig.SEGMENT_LEN_SECONDS

        eeg_class = ClassificationType.SEIZURE
        self.edf_processor.classification_type = eeg_class

        # WHEN & THEN
        self.edf_processor.config = EdfProcessorErrorTestConfig()
        self.assertRaises(ValueError, self.edf_processor._load_config)

    def test_normalize(self):
        # GIVEN
        with DATA_DIR.joinpath('test_normalize_array.json').open(mode='r') as f:
            test_data = json.load(f)['normalize']

        for i, params in enumerate(test_data):
            input_array = np.array(params['input'])
            output_array = np.array(params['expected_output'])
            min_val, max_val = params['min_val'], params['max_val']

            with self.subTest(test_num=i):
                self.edf_processor.edf_record.min_max_value = (min_val, max_val)

                # WHEN
                actual = self.edf_processor._normalize(input_array)

                # THEN
                np.testing.assert_array_equal(actual, output_array)

    def test_split_to_segments(self):
        # GIVEN
        with DATA_DIR.joinpath('test_split_segments.json').open() as f:
            test_data = json.load(f)['split_segments']

        # WHEN
        for i, params in enumerate(test_data):
            segment_len = params['segment_len']
            input_array = np.array(params['input'])
            sfreq = params['sfreq']
            expected_array = np.array(params['expected_output'])
            expected_segment_cuts = [tuple(val) for val in params['segment_cuts']]

            self.edf_processor.edf_record.to_numpy = MagicMock(return_value=input_array)

            with self.subTest(test_num=i, segment_len=segment_len):
                self.edf_processor.segment_len = segment_len
                self.edf_processor.edf_record.duration = input_array.shape[1]
                self.edf_processor.edf_record.sampling_frequency = sfreq
                actual_output = self.edf_processor._split_to_segments()

            # THEN
            np.testing.assert_array_equal(actual_output, expected_array)
            self.assertEqual(actual_output.shape[-1], segment_len * sfreq)
            self.assertListEqual(expected_segment_cuts, self.edf_processor.segment_cuts)

    def test_split_to_frames(self):
        # GIVEN
        with DATA_DIR.joinpath('test_split_frames.json').open() as f:
            test_data = json.load(f)['split_frames']

        # WHEN
        for i, params in enumerate(test_data):
            sfreq = params['sfreq']
            segment_len = params['segment_len']
            frame_amount = params['frame_amount']
            input_array = np.array(params['input'])
            expected_array = np.array(params['expected_output'])

            with self.subTest(test_num=i, frame_num=frame_amount):
                self.edf_processor.segment_len = segment_len
                self.edf_processor.edf_record.sampling_frequency = sfreq
                self.edf_processor.frame_len = segment_len / frame_amount

                actual_output = self.edf_processor._split_to_frames(segmented_array=input_array)

                # THEN
                np.testing.assert_array_equal(actual_output, expected_array)
                self.assertEqual(frame_amount, actual_output.shape[1])
                self.assertEqual(4, actual_output.ndim)
