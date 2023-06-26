from eeg_web_assistant.core.edf_file import ClassificationType, EdfFile, EdfProcessor
from eeg_web_assistant.ml.data_processing.eeg_features import FeatureExtractor
from tests.integration import IntegrationTestCase

DATA_DIR = IntegrationTestCase.FIXTURE_DIR.joinpath('edf_processing')


class EdfFileTestConfig:
    EDF_FILE_EXCLUDE = DATA_DIR.joinpath('edf_file_config_with_exclude.json')


class EdfProcessorTestConfig:
    EDF_CHANNELS_SETUP = DATA_DIR.joinpath('edf_file_classify_channels_correct.json')
    SEGMENT_LEN_SECONDS = 16
    TIMEFRAMES_AMOUNT = 8


class TestFeatureExtractor(IntegrationTestCase):

    def setUp(self) -> None:
        self.edf_file = EdfFile(path=DATA_DIR.joinpath('edf_file_seizure_all_channels.edf'),
                                config=EdfFileTestConfig())

        self.edf_processor = EdfProcessor(edf_record=self.edf_file,
                                          classification_type=ClassificationType.SEIZURE,
                                          config=EdfProcessorTestConfig())
        self.edf_processor._load_config()

        self.processed_array = self.edf_processor.process()

    def test_extract__return_correct_shape(self):
        # GIVEN
        segments, frames, channels, _ = self.processed_array.shape

        sfreq = self.edf_processor.edf_record.sampling_frequency
        bands = ['Delta', 'Theta', 'Alpha', 'Beta']

        self.feature_extractor = FeatureExtractor(array=self.processed_array,
                                                  sfreq=sfreq, bands=tuple(bands))
        # WHEN
        extracted_features = self.feature_extractor.extract()

        # THEN
        expected_shape = (segments, frames, channels, 7 + len(bands) + channels)
        self.assertTupleEqual(expected_shape, extracted_features.shape)
