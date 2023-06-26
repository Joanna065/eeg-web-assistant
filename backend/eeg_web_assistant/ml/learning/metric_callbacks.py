from typing import Any

import tensorflow as tf
from tensorflow.keras.metrics import Precision, Recall


class F1Score(tf.keras.metrics.Metric):
    def __init__(self, class_id: int = 0, name: str = 'f1score', **kwargs):
        super(F1Score, self).__init__(name=name, **kwargs)
        self.class_id = class_id

        self.recall = Recall(class_id=class_id, name=f'recall_{class_id}')
        self.precision = Precision(class_id=class_id, name=f'precision_{class_id}')

    def get_config(self):
        config = {
            'class_id': self.class_id,
            'name': self.name
        }
        return config

    def update_state(self, y_true: tf.Tensor, y_pred: tf.Tensor, sample_weight: Any = None):
        self.recall.update_state(y_true, y_pred)
        self.precision.update_state(y_true, y_pred)

    def result(self):
        precision = self.precision.result()
        recall = self.recall.result()
        return tf.multiply(2.0, tf.multiply(precision, recall) / tf.add(precision, recall))

    def reset_states(self):
        self.recall.reset_states()
        self.precision.reset_states()


class CategoricalPrecision(tf.keras.metrics.Metric):
    def __init__(self, class_amount: int, class_id: int, name: str = 'precision', **kwargs):
        super(CategoricalPrecision, self).__init__(name=name, **kwargs)

        self.class_id = class_id
        self.num_classes = class_amount
        self.total_cm = self.add_weight(name="total_confusion_matrix",
                                        shape=(class_amount, class_amount),
                                        initializer="zeros")

    def update_state(self, y_true: tf.Tensor, y_pred: tf.Tensor, sample_weight: Any = None):
        self.total_cm.assign_add(confusion_matrix(y_true, y_pred, self.num_classes))

    def result(self):
        cm = self.total_cm
        diag_part = tf.linalg.diag_part(cm)
        precision = diag_part / (tf.reduce_sum(cm, 0) + tf.constant(1e-15))
        return precision[self.class_id]

    def reset_states(self):
        for s in self.variables:
            s.assign(tf.zeros(shape=s.shape))


class CategoricalRecall(tf.keras.metrics.Metric):
    def __init__(self, class_amount: int, class_id: int, name: str = 'recall', **kwargs):
        super(CategoricalRecall, self).__init__(name=name, **kwargs)

        self.class_id = class_id
        self.num_classes = class_amount
        self.total_cm = self.add_weight(name="total_confusion_matrix",
                                        shape=(class_amount, class_amount),
                                        initializer="zeros")

    def update_state(self, y_true: tf.Tensor, y_pred: tf.Tensor, sample_weight: Any = None):
        self.total_cm.assign_add(confusion_matrix(y_true, y_pred, self.num_classes))

    def result(self):
        cm = self.total_cm
        diag_part = tf.linalg.diag_part(cm)
        recall = diag_part / (tf.reduce_sum(cm, 1) + tf.constant(1e-15))
        return recall[self.class_id]

    def reset_states(self):
        for s in self.variables:
            s.assign(tf.zeros(shape=s.shape))


class CategoricalF1Score(tf.keras.metrics.Metric):
    def __init__(self, class_amount: int, class_id: int, name: str = 'f1score', **kwargs):
        super(CategoricalF1Score, self).__init__(name=name, **kwargs)

        self.recall = CategoricalRecall(class_id=class_id, class_amount=class_amount,
                                        name=f'recall_{class_id}')
        self.precision = CategoricalPrecision(class_id=class_id, class_amount=class_amount,
                                              name=f'precision_{class_id}')

    def update_state(self, y_true: tf.Tensor, y_pred: tf.Tensor, sample_weight: Any = None):
        self.recall.update_state(y_true, y_pred)
        self.precision.update_state(y_true, y_pred)

    def result(self):
        precision = self.precision.result()
        recall = self.recall.result()
        f1score = 2 * precision * recall / (precision + recall + tf.constant(1e-15))
        return f1score

    def reset_states(self):
        self.recall.reset_states()
        self.precision.reset_states()


class CategoricalSpecificity(tf.keras.metrics.Metric):
    def __init__(self, class_amount: int, class_id: int, name: str = 'specificity', **kwargs):
        super(CategoricalSpecificity, self).__init__(name=name, **kwargs)

        self.class_id = class_id
        self.num_classes = class_amount
        self.total_cm = self.add_weight(name="total_confusion_matrix",
                                        shape=(class_amount, class_amount),
                                        initializer="zeros")

    def update_state(self, y_true: tf.Tensor, y_pred: tf.Tensor, sample_weight: Any = None):
        self.total_cm.assign_add(confusion_matrix(y_true, y_pred, self.num_classes))
        return self.total_cm

    def result(self):
        cm = self.total_cm
        tp = tf.linalg.diag_part(cm)
        fp = tf.reduce_sum(cm, 0) - tp
        fn = tf.reduce_sum(cm, 1) - tp
        tn = tf.reduce_sum(cm) - (fp + fn + tp)
        specificity = tn / (tn + fp + tf.constant(1e-15))
        return specificity[self.class_id]

    def reset_states(self):
        for s in self.variables:
            s.assign(tf.zeros(shape=s.shape))


def confusion_matrix(y_true: tf.Tensor, y_pred: tf.Tensor, num_classes: int) -> tf.Tensor:
    y_true = tf.argmax(y_true, axis=1)
    y_pred = tf.argmax(y_pred, axis=1)
    cm = tf.math.confusion_matrix(y_true, y_pred, dtype=tf.float32, num_classes=num_classes)
    return cm
