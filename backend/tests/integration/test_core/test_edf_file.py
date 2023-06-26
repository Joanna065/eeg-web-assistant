import json
from unittest.mock import MagicMock, patch

from mne.io.edf.edf import RawEDF

from eeg_web_assistant.core.classification_types import ClassificationType
from eeg_web_assistant.core.edf_file import EdfFile, EdfProcessor
from tests.integration import IntegrationTestCase

DATA_DIR = IntegrationTestCase.FIXTURE_DIR.joinpath('edf_processing')


class EdfFileTestConfig:
    EDF_FILE_EXCLUDE = DATA_DIR.joinpath('edf_file_config_with_exclude.json')


class EdfProcessorTestConfig:
    EDF_CHANNELS_SETUP = DATA_DIR.joinpath('edf_file_classify_channels_correct.json')
    SEGMENT_LEN_SECONDS = 16
    TIMEFRAMES_AMOUNT = 8


class TestEdfFile(IntegrationTestCase):

    @patch('eeg_web_assistant.core.edf_file.EdfFile._load', MagicMock())
    def setUp(self) -> None:
        self.edf_file = EdfFile(path=DATA_DIR.joinpath('edf_file_seizure_all_channels.edf'),
                                config=EdfFileTestConfig())

    def test_load__type_mne_rawEDF(self):
        # WHEN
        self.edf_file._load()

        # THEN
        self.assertIsInstance(self.edf_file.raw, RawEDF)

    def test_load__drop_exclude_channels_from_edf(self):
        # WHEN
        self.edf_file._load()

        # THEN
        self.assertFalse(any([channel in self.edf_file.raw.ch_names
                              for channel in self.edf_file.exclude_channels]))


class TestEdfProcessor(IntegrationTestCase):

    def setUp(self) -> None:
        self.edf_file = EdfFile(path=DATA_DIR.joinpath('edf_file_seizure_all_channels.edf'),
                                config=EdfFileTestConfig())

        self.edf_processor = EdfProcessor(edf_record=self.edf_file,
                                          classification_type=ClassificationType.SEIZURE,
                                          config=EdfProcessorTestConfig())

        self.edf_processor._load_config()

    def test_modify_for_classification__drop_channel_difference(self):
        # GIVEN
        with self.edf_processor.config.EDF_CHANNELS_SETUP.open(mode='r') as f:
            edf_chan_setup = json.load(f)

        common_channels = edf_chan_setup[self.edf_processor.classification_type.value]
        segment_len = self.edf_processor.segment_len
        duration = self.edf_file.raw.n_times / self.edf_file.raw.info['sfreq']
        expected_duration = segment_len * int(duration / segment_len)

        self.edf_file.channel_setup = common_channels

        # WHEN
        self.edf_processor._modify_for_classification()

        # THEN
        self.assertSetEqual(set(self.edf_processor.edf_record.channel_names), set(common_channels))
        self.assertEqual(self.edf_processor.edf_record.duration, expected_duration)

    def test_process__return_correct_shape(self):
        # GIVEN
        segment_len = self.edf_processor.config.SEGMENT_LEN_SECONDS
        frame_num = self.edf_processor.config.TIMEFRAMES_AMOUNT

        # WHEN
        processed_array = self.edf_processor.process()

        sfreq = self.edf_processor.edf_record.sampling_frequency
        channel_num = len(self.edf_processor.edf_record.channel_names)
        frame_times = int(segment_len / frame_num) * sfreq
        segment_num = self.edf_processor.edf_record.duration / segment_len

        # THEN
        expected_shape = (segment_num, frame_num, channel_num, frame_times)
        self.assertTupleEqual(processed_array.shape, expected_shape)
