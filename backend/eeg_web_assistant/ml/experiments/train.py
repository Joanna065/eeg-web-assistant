import json
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Tuple

import numpy as np
import tensorflow as tf
from tensorflow.python.keras.utils.np_utils import to_categorical

from eeg_web_assistant import settings
from eeg_web_assistant.ml.experiments.model_dump import save_model_summary
from eeg_web_assistant.services.logging import Logging

logger = Logging.get(__name__)

date = datetime.today()
date_now = date.strftime('%Y-%m-%d_%H-%M')


def train_model(model_fun: Callable, model_params: Dict, train_params: Dict, data: Tuple[
    np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray], model_name: str,
                dataset_name: str, class_amount: int, custom: bool = False):
    x_train, y_train, x_val, y_val, x_test, y_test = data

    y_train = to_categorical(y_train, num_classes=class_amount)
    y_val = to_categorical(y_val, num_classes=class_amount)
    y_test = to_categorical(y_test, num_classes=class_amount)

    save_filename = f'{date_now}_{model_name}-{dataset_name}-epochs-{train_params["epochs"]}'

    checkpoint_path = settings.ModelTrain.CHECKPOINT_DIR / f'{save_filename}.ckpt'

    tb_dir = settings.ModelTrain.LOGS_DIR / save_filename
    Path.mkdir(tb_dir, parents=True, exist_ok=True)

    # callbacks
    tensorboard = tf.keras.callbacks.TensorBoard(log_dir=tb_dir, update_freq='epoch')
    early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)

    model_checkpoint = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                          save_weights_only=True,
                                                          monitor='val_loss',
                                                          mode='min',
                                                          patience=10,
                                                          save_best_only=True,
                                                          verbose=1)

    model = model_fun(**model_params)
    model.compile(loss=train_params['loss'],
                  optimizer=train_params['optimizer'],
                  metrics=train_params['metrics'])

    with (settings.ModelTrain.MODEL_DUMP_CONFIG_DIR / f'{save_filename}.json').open(mode='w') as f:
        config = model.get_config()
        json.dump(config, f)

    logger.info("Training model %s... ", model_name)
    model.fit(x_train, y_train,
              epochs=train_params['epochs'],
              batch_size=train_params['batch_size'],
              validation_data=(x_val, y_val),
              shuffle=True,
              verbose=1,
              callbacks=[model_checkpoint, early_stop, tensorboard])

    logger.info('Evaluating model... ')
    model.load_weights(checkpoint_path)
    model.evaluate(x_test, y_test, verbose=1)

    logger.info("Saving model dump...")
    if custom:
        model.save(filepath=settings.ModelTrain.MODEL_DUMP_DIR / save_filename, save_format='tf')
    else:
        model.save(filepath=settings.ModelTrain.MODEL_DUMP_DIR / f'{save_filename}.h5')

    save_model_summary(path=settings.ModelTrain.MODEL_DUMP_DIR / f'{save_filename}.txt',
                       model=model)
