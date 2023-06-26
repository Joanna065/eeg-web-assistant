from pathlib import Path

import tensorflow as tf


def save_model_summary(path: Path, model: tf.keras.Model):
    with path.open(mode='w') as f:
        model.summary(print_fn=lambda x: f.write(x + '\n'))
