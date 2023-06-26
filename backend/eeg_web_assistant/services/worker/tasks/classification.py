from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Tuple

import numpy as np
from bson import ObjectId
from celery import current_app

from eeg_web_assistant.core.classification_types import ClassificationType
from eeg_web_assistant.core.edf_file import EdfFile, EdfProcessor
from eeg_web_assistant.core.process_classification_results import ClassificationResults
from eeg_web_assistant.ml.predictors.predict import predict_eeg_proba_per_segment
from eeg_web_assistant.models.recording import ClassificationInfoInDB, ClassificationSegmentInDB
from eeg_web_assistant.services.database import Database
from eeg_web_assistant.utils.dict import get_dict_with_prefix_keys


@current_app.task(name='tasks.classification.classify_recording', serializer='pickle')
def classify_recording(recording_id: str, raw_data_id: str, classification_type: str,
                       ch_names: List[str], sfreq: float):
    raw_data = Database().recordings_raw.get(ObjectId(raw_data_id))

    raw_array, processed_array, segment_cuts = _process_edf(
        edf_data=raw_data, class_type=ClassificationType(classification_type)
    )

    proba_mean, proba_std = predict_eeg_proba_per_segment(
        eeg_array=processed_array,
        classification_type=ClassificationType(classification_type),
        sfreq=sfreq
    )

    results_obj = ClassificationResults(raw_array=raw_array, proba_mean=proba_mean,
                                        proba_std=proba_std, segment_cuts=segment_cuts,
                                        ch_names=ch_names, sfreq=sfreq)

    classified_segments = [ClassificationSegmentInDB(**val) for val in results_obj.process()]
    classification_info = ClassificationInfoInDB(
        type=ClassificationType(classification_type),
        segments=classified_segments
    )

    Database().recordings_data.find_one_by_id_and_update(
        id_=ObjectId(recording_id),
        update_data=get_dict_with_prefix_keys(
            dictionary=classification_info.dict(exclude_unset=True),
            prefix=f'classification.{classification_type}.')
    )

    return classification_info.dict(exclude_unset=True)


def _process_edf(edf_data: bytes,
                 class_type: ClassificationType
                 ) -> Tuple[np.ndarray, np.ndarray, List[Tuple[int, int]]]:
    with NamedTemporaryFile(suffix='.edf') as tf:
        tf.write(edf_data)
        edf_file = EdfFile(path=Path(tf.name))
        raw_array = edf_file.to_numpy()

        edf_processor = EdfProcessor(edf_record=edf_file, classification_type=class_type)
        processed_array = edf_processor.process()
        segment_cuts = edf_processor.segment_cuts

    return raw_array, processed_array, segment_cuts
