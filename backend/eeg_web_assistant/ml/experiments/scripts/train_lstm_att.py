import json
from datetime import datetime

import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.python.keras.metrics import Precision, Recall

from eeg_web_assistant import settings
from eeg_web_assistant.ml.data_processing.io_utils import open_dataset
from eeg_web_assistant.ml.experiments.train import train_model
from eeg_web_assistant.ml.learning.metric_callbacks import F1Score
from eeg_web_assistant.ml.models.lstm_att import AttentionLSTM

DATASET_TRAIN_PATH = settings.DatasetConfig.ABNORMAL_TRAIN
DATASET_TEST_PATH = settings.DatasetConfig.ABNORMAL_TEST
DATASET_NAME = DATASET_TRAIN_PATH.stem.replace('_train', '')

date = datetime.today()
date_now = date.strftime('%Y-%m-%d_%H-%M')

# load train data and split to train-val
x_train, y_train, labels_encoder, common_channels = open_dataset(DATASET_TRAIN_PATH)
amount, timeframes, channels, features = x_train.shape

x_train = x_train.reshape((amount, timeframes, channels * features))
x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=0.1, shuffle=True,
                                                  stratify=y_train)

# load test data
x_test, y_test, _, _ = open_dataset(DATASET_TEST_PATH)

split_data = x_train, y_train, x_val, y_val, x_test, y_test

class_amount = len(np.sort(np.unique(y_train)))

with settings.ModelHParams.LSTM_ATT_HPARAMS.open(mode='r') as f:
    hparams = json.load(f)

cm_metrics = [(Recall(class_id=nr, name=f'recall_{nr}'),
               Precision(class_id=nr, name=f'precision_{nr}'),
               F1Score(class_id=nr, name=f'f1score_{nr}')) for nr in range(class_amount)]

cm_metrics = [item for sublist in cm_metrics for item in sublist]

model_params = {
    'num_classes': class_amount,
    'hidden_units': hparams['hidden_units'],
    'd0': hparams['dropout_0'],
    'd1': hparams['dropout_1'],
    'd2': hparams['dropout_2'],
    'l2': hparams['l2'],
    'timesteps': timeframes
}

train_params = {
    'batch_size': 32,
    'epochs': 200,
    'loss': 'categorical_crossentropy',
    'optimizer': tf.keras.optimizers.Adam(learning_rate=hparams["lr"]),
    'metrics': ['accuracy', *cm_metrics]
}
# prepare save directory name
MODEL_NAME = 'LSTMAtt'

# get model
train_model(model_fun=AttentionLSTM, model_params=model_params, train_params=train_params,
            data=split_data, model_name=MODEL_NAME, dataset_name=DATASET_NAME,
            class_amount=class_amount, custom=True)
