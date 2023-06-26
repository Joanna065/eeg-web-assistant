from sklearn.model_selection import train_test_split

from eeg_web_assistant import settings
from eeg_web_assistant.ml.data_processing.io_utils import open_dataset, save_dataset

DATASET_PATH = settings.DatasetConfig.ABNORMAL_TWO_CLASS
DATASET_NAME = DATASET_PATH.stem

# load data
data, labels, labels_encoder, common_channels = open_dataset(DATASET_PATH)
x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.1, shuffle=True,
                                                    stratify=labels)

save_dataset(filepath=settings.DATA_DIR / 'split' / (DATASET_NAME + '_train.pkl'),
             data=x_train,
             labels=y_train,
             labels_encoder=labels_encoder,
             common_channels=common_channels)

save_dataset(filepath=settings.DATA_DIR / 'split' / (DATASET_NAME + '_test.pkl'),
             data=x_test,
             labels=y_test,
             labels_encoder=labels_encoder,
             common_channels=common_channels)
