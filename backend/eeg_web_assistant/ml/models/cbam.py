from typing import Tuple

import tensorflow as tf


def build_cbam_model(shape: Tuple[int, int, int, int], class_num: int, hidden_units: int = 256,
                     dropout: float = 0.15, filters: int = 32, kernel: int = 3,
                     reduce_ratio: int = 16, spatial_kernel: int = 7) -> tf.keras.Model:
    assert len(shape) == 4
    batch_size, timeframes, channels, features = shape

    input_0 = tf.keras.Input((timeframes, channels, features))

    layers = []
    for frame in range(timeframes):
        frame_matrix = tf.keras.layers.Lambda(
            get_frame,
            arguments={'frame': frame, 'channels': channels, 'features': features}
        )(input_0)

        x = tf.keras.layers.Conv1D(filters, kernel, data_format='channels_first')(frame_matrix)
        x = cbam_module(x, reduction_ratio=reduce_ratio, spatial_kernel=spatial_kernel)
        x = tf.keras.layers.Flatten()(x)

        layers.append(x)

    combine = tf.keras.layers.Concatenate()(layers)
    reshape = tf.keras.layers.Reshape((timeframes, -1))(combine)
    lstm = tf.keras.layers.LSTM(hidden_units)(reshape)
    dropout = tf.keras.layers.Dropout(dropout)(lstm)
    out = tf.keras.layers.Dense(class_num, activation='softmax')(dropout)

    return tf.keras.Model(inputs=[input_0], outputs=out)


def get_frame(x, frame, channels, features):
    x = tf.slice(x, [0, frame, 0, 0], [-1, 1, channels, features])
    x = tf.squeeze(x, axis=[1])
    return x


def channel_attention(inputs, reduction_ratio: int = 8):
    assert len(inputs.shape) == 3, 'Channel attention input must have 3 dims!'
    _, channels, features = inputs.shape

    def shared_mlp(input_att, channel: int, ratio: int):
        reduced = tf.keras.layers.Dense(units=channel // ratio,
                                        activation='relu',
                                        kernel_initializer='glorot_uniform',
                                        use_bias=True,
                                        bias_initializer='zeros')(input_att)
        assert reduced.shape[1] == channel // ratio

        out = tf.keras.layers.Dense(units=channel,
                                    activation='relu',
                                    kernel_initializer='glorot_uniform',
                                    use_bias=True,
                                    bias_initializer='zeros')(reduced)
        assert out.shape[1] == channel
        return out

    avg_pool = tf.keras.layers.GlobalAveragePooling1D(data_format='channels_first')(inputs)
    assert avg_pool.shape[1] == channels

    avg_pool = shared_mlp(avg_pool, channel=channels, ratio=reduction_ratio)
    avg_pool = tf.keras.layers.Reshape((channels, 1))(avg_pool)

    max_pool = tf.keras.layers.GlobalMaxPool1D(data_format='channels_first')(inputs)
    assert max_pool.shape[1] == channels

    max_pool = shared_mlp(max_pool, channel=channels, ratio=reduction_ratio)
    max_pool = tf.keras.layers.Reshape((channels, 1))(max_pool)

    channel_att = tf.keras.layers.Add()([avg_pool, max_pool])
    channel_att = tf.keras.layers.Activation('sigmoid')(channel_att)

    assert len(channel_att.shape) == len(inputs.shape)

    return tf.keras.layers.Multiply()([inputs, channel_att])


def spatial_attention(inputs, kernel_size=7):
    assert len(inputs.shape) == 3, 'Spatial attention input must have 3 dims!'
    _, channels, features = inputs.shape

    def reduce_mean(input_layer):
        return tf.reduce_mean(input_layer, axis=1, keepdims=True)

    def reduce_max(input_layer):
        return tf.reduce_max(input_layer, axis=1, keepdims=True)

    avg_pool = tf.keras.layers.Lambda(function=reduce_mean)(inputs)
    assert avg_pool.shape[-1] == features

    max_pool = tf.keras.layers.Lambda(function=reduce_max)(inputs)
    assert max_pool.shape[-1] == features

    concat = tf.keras.layers.Concatenate(axis=1)([avg_pool, max_pool])
    assert concat.shape[1] == 2

    spatial_att = tf.keras.layers.Conv1D(filters=1,
                                         kernel_size=kernel_size,
                                         strides=1,
                                         data_format='channels_first',
                                         padding='same',
                                         activation='sigmoid',
                                         kernel_initializer='glorot_uniform',
                                         use_bias=False)(concat)
    assert spatial_att.shape[1] == 1
    assert len(spatial_att.shape) == len(inputs.shape)

    return tf.keras.layers.Multiply()([inputs, spatial_att])


def cbam_module(inputs, reduction_ratio: int = 16, spatial_kernel: int = 7):
    cbam_features = channel_attention(inputs, reduction_ratio)
    cbam_features = spatial_attention(cbam_features, kernel_size=spatial_kernel)

    return cbam_features
