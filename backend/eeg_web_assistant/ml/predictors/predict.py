from typing import Optional

import numpy as np

from eeg_web_assistant.core.classification_types import ClassificationType
from eeg_web_assistant.ml.data_processing.eeg_features import FeatureExtractor
from eeg_web_assistant.ml.models import Model


def predict_eeg_proba_per_segment(eeg_array: np.ndarray, classification_type: ClassificationType,
                                  sfreq: float):
    features = _extract_features(eeg_array=eeg_array, sfreq=sfreq)

    probs_mean, probs_std = _predict_proba(features, class_type=classification_type, batch_size=32)

    return probs_mean, probs_std


def _extract_features(eeg_array: np.ndarray, sfreq: float) -> np.ndarray:
    feature_extractor = FeatureExtractor(array=eeg_array, sfreq=sfreq,
                                         bands=('Delta', 'Theta', 'Alpha', 'Beta'))

    return feature_extractor.extract()


def _predict_proba(input_data: np.ndarray, class_type: ClassificationType, batch_size: int = 32,
                   monte_carlo_iter: int = 100, class_id: int = 1):
    model = Model.load(class_type)

    pred_probs = []
    for i in range(monte_carlo_iter):
        probs = model.predict(input_data, batch_size=batch_size)
        probs = [prob[class_id] for prob in probs]
        pred_probs.append(probs)

    pred_probs = np.stack(pred_probs)

    return pred_probs.mean(axis=0), pred_probs.std(axis=0)


def _predict_classes(probs: np.ndarray, variance: np.ndarray, prob_threshold: float = 0.5,
                     std_threshold: Optional[float] = None):
    classes = np.where(probs > prob_threshold, 1, 0)

    if std_threshold:
        std_classes = np.where(variance < std_threshold, 1, 0)
        classes = np.multiply(classes, std_classes)

    return classes, variance
