import json
from pathlib import Path

import tensorflow as tf

from eeg_web_assistant import settings
from eeg_web_assistant.core.classification_types import ClassificationType
from eeg_web_assistant.ml.models.insta_gat import InstaGAT


class Model:
    _ABNORMAL_MODEL = None
    _ARTIFACT_MODEL = None
    _SEIZURE_MODEL = None

    @classmethod
    def load(cls, class_type: ClassificationType,
             monte_carlo: bool = True) -> tf.keras.models.Model:
        name = class_type.value

        if name == 'abnormal':
            if cls._ABNORMAL_MODEL is None:
                cls._ABNORMAL_MODEL = cls._get_model(
                    config_path=settings.ModelPredict.ABNORMAL_CONFIG,
                    model_weights_path=settings.ModelPredict.ABNORMAL_WEIGHTS,
                    monte_carlo=monte_carlo)

            return cls._ABNORMAL_MODEL

        elif name == 'artifact':
            if cls._ARTIFACT_MODEL is None:
                cls._ARTIFACT_MODEL = cls._get_model(
                    config_path=settings.ModelPredict.ARTIFACT_CONFIG,
                    model_weights_path=settings.ModelPredict.ARTIFACT_WEIGHTS,
                    monte_carlo=monte_carlo)

            return cls._ARTIFACT_MODEL

        elif name == 'seizure':
            if cls._SEIZURE_MODEL is None:
                cls._SEIZURE_MODEL = cls._get_model(
                    config_path=settings.ModelPredict.SEIZURE_CONFIG,
                    model_weights_path=settings.ModelPredict.SEIZURE_WEIGHTS,
                    monte_carlo=monte_carlo)

            return cls._SEIZURE_MODEL

        else:
            raise ValueError(f"Unsupported model type: {name}")

    @staticmethod
    def _get_model(config_path: Path, model_weights_path: Path,
                   monte_carlo: bool = True) -> tf.keras.models.Model:
        with config_path.open(mode='r') as f:
            model_params = json.load(f)

        model = InstaGAT(**model_params)
        model.monte_carlo = monte_carlo
        model.load_weights(model_weights_path)

        return model
