import tensorflow as tf
from tensorflow.keras import regularizers


class AttentionLSTM(tf.keras.Model):
    def __init__(self, num_classes: int, hidden_units: int = 128, d0: float = 0.1,
                 d1: float = 0.2, d2: float = 0.2, l2: float = 0.001, timesteps=8,
                 name='lstm_attention', **kwargs):
        super(AttentionLSTM, self).__init__(name=name, **kwargs)
        self.num_classes = num_classes
        self.timesteps = timesteps

        self.input_dropout = tf.keras.layers.Dropout(rate=d0)
        self.lstm_1 = tf.keras.layers.LSTM(hidden_units,
                                           return_sequences=True,
                                           name='lstm_1',
                                           activation='tanh',
                                           dropout=d1,
                                           kernel_regularizer=regularizers.l2(l2))
        self.lstm_2 = tf.keras.layers.LSTM(hidden_units,
                                           return_sequences=True,
                                           name='lstm_2',
                                           activation='tanh',
                                           dropout=d2,
                                           kernel_regularizer=regularizers.l2(l2))
        self.attention = AttentionLayer(units=self.timesteps,
                                        name='attention',
                                        activation=None,
                                        use_bias=True)
        self.classifier = tf.keras.layers.Dense(units=self.num_classes,
                                                name='dense_classifier',
                                                activation='softmax')

    def get_config(self):
        config = {
            'num_classes': self.num_classes,
            'name': self.name,
            'd0': self.d0,
            'd1': self.d1,
            'd2': self.d2,
            'hidden_units': self.hidden_units,
            'l2': self.l2,
            'timesteps': self.timesteps
        }
        return config

    def call(self, inputs, **kwargs):
        x = self.input_dropout(inputs)
        x = self.lstm_1(x)
        x = self.lstm_2(x)
        x = self.attention(x)
        return self.classifier(x)

    def build_graph(self, input_shape):
        input_shape_nobatch = input_shape[1:]
        self.build(input_shape)
        inputs = tf.keras.Input(shape=input_shape_nobatch)

        if not hasattr(self, 'call'):
            raise AttributeError('User should define "call" methods in subclass model')

        _ = self.call(inputs)


class AttentionLayer(tf.keras.layers.Layer):
    def __init__(self,
                 units,
                 name=None,
                 activation=None,
                 use_bias=True,
                 kernel_initializer='glorot_uniform',
                 bias_initializer='zeros'):
        super(AttentionLayer, self).__init__(name=name)
        self.units = units  # timesteps
        self.activation = tf.keras.activations.get(activation)
        self.use_bias = use_bias
        self.kernel_initializer = tf.keras.initializers.get(kernel_initializer)
        self.bias_initializer = tf.keras.initializers.get(bias_initializer)
        self.input_spec = tf.keras.layers.InputSpec(ndim=3)

    def get_config(self):
        config = {
            'name': self.name,
            'units': self.units,
            'activation': self.activation,
            'use_bias': self.use_bias,
            'kernel_initializer': self.kernel_initializer,
            'bias_initializer': self.bias_initializer
        }
        return config

    def build(self, input_shape):
        """
        :param input_shape: 3D tensor (batch_size, timesteps, features)
        :return:
        """
        self.kernel = self.add_weight(
            'kernel',
            shape=[1, input_shape[-1]],
            initializer=self.kernel_initializer,
            dtype=self.dtype,
            trainable=True)

        if self.use_bias:
            self.bias = self.add_weight(
                'bias',
                shape=[self.units, ],
                initializer=self.bias_initializer,
                dtype=self.dtype,
                trainable=True)
        else:
            self.bias = None

    def call(self, inputs, **kwargs):
        # change dim to (batch_size, hidden_units, timesteps)
        inputs = tf.transpose(inputs, perm=[0, 2, 1])
        U = tf.matmul(self.kernel, inputs)

        if self.use_bias:
            U = tf.nn.bias_add(U, self.bias)

        U = tf.math.tanh(U)
        alpha = tf.nn.softmax(U)
        outputs = tf.math.reduce_sum(tf.math.multiply(alpha, inputs), axis=1)
        return outputs
