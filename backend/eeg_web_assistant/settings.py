from dataclasses import dataclass
from os import getenv
from pathlib import Path

# PATHS
PROJECT_DIR = Path(__file__).parent.parent
STORAGE_DIR = PROJECT_DIR / '.storage'
DB_SAMPLES_DIR = STORAGE_DIR / 'edf_samples'
CONFIG_DIR = STORAGE_DIR / 'configs'

DATA_DIR = STORAGE_DIR / 'data'
HPARAMS_DIR = PROJECT_DIR / 'eeg_web_assistant' / 'ml' / 'experiments' / 'hparams'
MODEL_WEIGHTS_DIR = STORAGE_DIR / 'checkpoints'
MODEL_CONFIG_DIR = STORAGE_DIR / 'configs' / 'models'


# CONFIGS
@dataclass(init=False, frozen=True)
class LoggingConfig:
    PATH = STORAGE_DIR / 'configs' / 'logging.yml'
    LOG_DIR = STORAGE_DIR / 'logs'


@dataclass(init=False, frozen=True)
class APIConfig:
    ROOT_PATH = None
    TITLE = "EEG Web Assistant"
    DESCRIPTION = "Web application for EEG signal classification"


@dataclass(init=False, frozen=True)
class WorkerConfig:
    broker_url = 'pyamqp://guest@localhost:5672'
    result_backend = 'rpc://'
    task_track_started = True
    worker_hijack_root_logger = False
    task_serializer = 'pickle'
    accept_content = {'pickle', 'json'}


@dataclass(init=False, frozen=True)
class EdfFileConfig:
    EDF_FILE_EXCLUDE = STORAGE_DIR / 'configs' / 'edf' / 'edf_file_exclude_channels.json'
    MAX_DURATION_MINUTES = 30


@dataclass(init=False, frozen=True)
class EdfProcessingConfig:
    SEGMENT_LEN_SECONDS = 16
    TIMEFRAMES_AMOUNT = 8
    EDF_CHANNELS_SETUP = STORAGE_DIR / 'configs' / 'edf' / 'edf_classify_channels.json'


@dataclass(init=False, frozen=True)
class PlotConfig:
    FRAGMENT_DURATION_SECONDS = 64
    MAX_SAMPLING_FREQUENCY = 200
    IMG_FORMAT = 'svg'
    FONT_SIZE = 9
    WIDTH = 800
    HEIGHT = 600
    PADDINGS_LRTB = (90, 20, 20, 20)


@dataclass(init=False, frozen=True)
class DatasetConfig:
    ABNORMAL_PROCESSED = DATA_DIR / 'processed' / 'tuheeg_abnormal.pkl'
    ARTIFACT_PROCESSED = DATA_DIR / 'processed' / 'tuheeg_artifact.pkl'
    SEIZURE_PROCESSED = DATA_DIR / 'processed' / 'tuheeg_seizure.pkl'

    ABNORMAL_TWO_CLASS = DATA_DIR / 'processed' / 'tuheeg_abnormal_2class.pkl'
    ARTIFACT_TWO_CLASS = DATA_DIR / 'processed' / 'tuheeg_artifact_2class.pkl'
    SEIZURE_TWO_CLASS = DATA_DIR / 'processed' / 'tuheeg_seizure_2class.pkl'

    ABNORMAL_TRAIN = DATA_DIR / 'split' / 'tuheeg_abnormal_2class_train.pkl'
    ABNORMAL_TEST = DATA_DIR / 'split' / 'tuheeg_abnormal_2class_test.pkl'
    ARTIFACT_TRAIN = DATA_DIR / 'split' / 'tuheeg_artifact_2class_train.pkl'
    ARTIFACT_TEST = DATA_DIR / 'split' / 'tuheeg_artifact_2class_test.pkl'
    SEIZURE_TRAIN = DATA_DIR / 'split' / 'tuheeg_seizure_2class_train.pkl'
    SEIZURE_TEST = DATA_DIR / 'split' / 'tuheeg_seizure_2class_test.pkl'

    SAMPLES_DIR = STORAGE_DIR / 'data' / 'samples'


@dataclass(init=False, frozen=True)
class ModelHParams:
    LSTM_ATT_HPARAMS = HPARAMS_DIR / 'hparams_lstm_att.json'
    GAT_HPARAMS = HPARAMS_DIR / 'hparams_gat.json'
    CBAM_HPARAMS = HPARAMS_DIR / 'hparams_cbam.json'


@dataclass(init=False, frozen=True)
class ModelTrain:
    CHECKPOINT_DIR = STORAGE_DIR / 'checkpoints'
    LOGS_DIR = STORAGE_DIR / 'logs'
    MODEL_DUMP_DIR = MODEL_WEIGHTS_DIR
    MODEL_DUMP_CONFIG_DIR = MODEL_CONFIG_DIR


@dataclass(init=False, frozen=True)
class ModelPredict:
    ABNORMAL_WEIGHTS = MODEL_WEIGHTS_DIR.joinpath(
        '2020-10-24_02-40_instaGAT-tuheeg_abnormal_2class-epochs-200.ckpt')
    ABNORMAL_CONFIG = MODEL_CONFIG_DIR.joinpath(
        '2020-10-24_02-40_instaGAT-tuheeg_abnormal_2class-epochs-200.json')

    ARTIFACT_WEIGHTS = MODEL_WEIGHTS_DIR.joinpath(
        '2020-10-24_02-47_instaGAT-tuheeg_artifact_2class-epochs-200.ckpt')
    ARTIFACT_CONFIG = MODEL_CONFIG_DIR.joinpath(
        '2020-10-24_02-47_instaGAT-tuheeg_artifact_2class-epochs-200.json')

    SEIZURE_WEIGHTS = MODEL_WEIGHTS_DIR.joinpath(
        '2020-10-24_02-52_instaGAT-tuheeg_seizure_2class-epochs-200.ckpt')
    SEIZURE_CONFIG = MODEL_CONFIG_DIR.joinpath(
        '2020-10-24_02-52_instaGAT-tuheeg_seizure_2class-epochs-200.json')


@dataclass(init=False, frozen=True)
class TestConfig:
    FIXTURE_DIR = PROJECT_DIR / 'tests' / 'fixtures'
    INTEGRATION = True


@dataclass(init=False, frozen=True)
class DatabaseConfig:
    NAME = 'eeg_web_assistant'
    ADDRESS = 'mongodb://localhost:27017'
    DB_NAME = 'eeg_assistant'
    USER_COLLECTION = 'user'
    RECORDING_DATA_COLLECTION = 'edf_recording_data'
    RECORDING_RAW_COLLECTION = 'edf_raw'


@dataclass(init=False, frozen=True)
class SecurityConfig:
    TOKEN_URL = '/auth/token'
    SECRET_KEY = '93d1a3e53fc57cefe2a09f59a7f0a462115a7f60a57169c106be28371c0eb8e1'
    ALGORITHM = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # a day


# SETUP ENVIRONMENT
ENVIRONMENT = getenv('EEG_WEB_ASSISTANT_ENVIRONMENT', default='default')

if ENVIRONMENT == 'production':
    APIConfig.ROOT_PATH = '/api'

    DatabaseConfig.ADDRESS = 'mongodb://database:27017'

    SecurityConfig.TOKEN_URL = '/api/auth/token'

    WorkerConfig.broker_url = 'pyamqp://guest@broker:5672'
