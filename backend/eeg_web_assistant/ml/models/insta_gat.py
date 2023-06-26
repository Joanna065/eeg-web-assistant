from typing import Optional, Tuple

import spektral as sp
import tensorflow as tf


class InstaGAT(tf.keras.Model):

    def __init__(self, dims: Tuple[int, int, int], class_num: int, output_channels: int = 64,
                 hidden_units: int = 64, dropout: float = 0.2, monte_carlo: bool = False,
                 name='instaGAT', **kwargs):
        super(InstaGAT, self).__init__(name=name, **kwargs)

        self.monte_carlo = monte_carlo
        self.hidden_units = hidden_units
        self.dropout = dropout
        self.output_channels = output_channels
        self.class_num = class_num
        self.dims = dims

        self.frames = dims[0]
        self.channels = dims[1]
        self.features = dims[2] - self.channels

        for frame in range(self.frames):
            feature_matrix = tf.keras.layers.Lambda(
                self.get_feature_matrix,
                arguments={'frame_num': frame, 'channels': self.channels, 'features': self.features}
            )
            correlation_matrix = tf.keras.layers.Lambda(
                self.get_correlation_matrix,
                arguments={'frame_num': frame, 'channels': self.channels}
            )
            graph = sp.layers.GraphAttention(self.output_channels)
            flatten = tf.keras.layers.Flatten()

            setattr(self, f'feature_matrix_{frame}', feature_matrix)
            setattr(self, f'correlation_matrix_{frame}', correlation_matrix)
            setattr(self, f'graph_{frame}', graph)
            setattr(self, f'flatten_{frame}', flatten)

        self.concatenate = tf.keras.layers.Concatenate()
        self.reshape = tf.keras.layers.Reshape((self.frames, self.channels * output_channels))
        self.lstm = tf.keras.layers.LSTM(hidden_units)
        self.dropout_layer = tf.keras.layers.Dropout(dropout)
        self.classifier = tf.keras.layers.Dense(class_num, activation='softmax')

    def call(self, inputs: tf.Tensor, training: Optional[bool] = None, **kwargs):
        layers = []
        for frame in range(self.frames):
            feature_matrix = getattr(self, f'feature_matrix_{frame}')(inputs)
            correlation_matrix = getattr(self, f'correlation_matrix_{frame}')(inputs)
            graph = getattr(self, f'graph_{frame}')([feature_matrix, correlation_matrix])
            flatten = getattr(self, f'flatten_{frame}')(graph)
            layers.append(flatten)

        x = self.concatenate(layers)
        x = self.reshape(x)
        x = self.lstm(x)
        x = self.dropout_layer(x, training=self.monte_carlo or training)

        return self.classifier(x)

    def get_config(self):
        config = {
            'dims': self.dims,
            'class_num': self.class_num,
            'output_channels': self.output_channels,
            'hidden_units': self.hidden_units,
            'dropout': self.dropout,
            'monte_carlo': self.monte_carlo,
            'name': self.name
        }
        return config

    @staticmethod
    def get_feature_matrix(x: tf.Tensor, frame_num: int, channels: int, features: int) -> tf.Tensor:
        x = tf.slice(x, [0, frame_num, 0, channels], [-1, 1, channels, features])
        x = tf.squeeze(x, axis=[1])
        return x

    @staticmethod
    def get_correlation_matrix(x: tf.Tensor, frame_num: int, channels: int) -> tf.Tensor:
        x = tf.slice(x, [0, frame_num, 0, 0], [-1, 1, channels, channels])
        x = tf.squeeze(x, axis=[1])
        return x
