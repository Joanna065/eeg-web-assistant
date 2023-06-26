from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from eeg_web_assistant.core.classification_types import ClassificationType
from eeg_web_assistant.models.recording import (ClassificationInfoInDB, ClassificationSegmentInDB,
                                                RecordingDataInDB)
from eeg_web_assistant.models.task import TaskStatus
from eeg_web_assistant.models.user import UserInDB
from eeg_web_assistant.services.api.routers.recording import _get_recording
from eeg_web_assistant.services.database import Database
from eeg_web_assistant.services.logging import Logging
from eeg_web_assistant.services.worker import Worker
from eeg_web_assistant.utils.bson import PyObjectId
from eeg_web_assistant.utils.exceptions import ExceptionModel, NonExistingClassificationError
from eeg_web_assistant.utils.security import get_current_user

logger = Logging.get(__name__)

router = APIRouter()


@router.patch('/{recording_id}',
              status_code=status.HTTP_202_ACCEPTED,
              responses={status.HTTP_200_OK: {"model": ExceptionModel},
                         status.HTTP_401_UNAUTHORIZED: {"model": ExceptionModel},
                         status.HTTP_403_FORBIDDEN: {"model": ExceptionModel},
                         status.HTTP_404_NOT_FOUND: {"model": ExceptionModel}})
def enqueue_classification_for_task_id(recording_id: PyObjectId,
                                       classification_type: ClassificationType,
                                       user: UserInDB = Depends(get_current_user),
                                       db: Database = Depends(Database),
                                       worker: Worker = Depends(Worker)):
    logger.debug("Enqueue classification task for recording id {%s} called by user {%s}",
                 recording_id, user.username)

    recording = RecordingDataInDB(**_get_recording(id_=recording_id, username=user.username, db=db))

    if recording.classification:
        classification_info = recording.classification.get(classification_type.value)

        if classification_info:
            json_segments = jsonable_encoder(classification_info.segments)
            return JSONResponse(status_code=status.HTTP_200_OK,
                                content=json_segments)

    try:
        task = worker.classification.classify_recording.delay(
            recording_id=str(recording_id),
            raw_data_id=str(recording.raw_id),
            classification_type=classification_type.value,
            ch_names=recording.recording_info.ch_names,
            sfreq=recording.recording_info.sfreq
        )
    except worker.classification.classify_recording.OperationalError as exc:
        logger.exception("Sending classify task raised: %r", exc)
    else:
        return task.id


@router.get('/{task_id}',
            response_model=TaskStatus,
            responses={status.HTTP_401_UNAUTHORIZED: {"model": ExceptionModel}})
def get_classification_status(task_id: str, user: UserInDB = Depends(get_current_user),
                              worker: Worker = Depends(Worker)):
    logger.debug("Get status for task id {%s} called by user {%s}", task_id, user.username)

    task = worker.get_task(task_id=task_id)
    result = task.result

    if task.status == 'SUCCESS':
        result = ClassificationInfoInDB(**task.result).segments

    return TaskStatus(task_id=task_id, status=task.status, result=result)


@router.get('/{recording_id}/report',
            response_model=List[ClassificationSegmentInDB],
            responses={status.HTTP_400_BAD_REQUEST: {"model": ExceptionModel},
                       status.HTTP_401_UNAUTHORIZED: {"model": ExceptionModel},
                       status.HTTP_403_FORBIDDEN: {"model": ExceptionModel},
                       status.HTTP_404_NOT_FOUND: {"model": ExceptionModel}})
def get_classification_report(recording_id: PyObjectId,
                              classification_type: ClassificationType,
                              min_prob: float,
                              max_std: Optional[float] = Query(None),
                              user: UserInDB = Depends(get_current_user),
                              db: Database = Depends(Database)):
    logger.debug(
        "Get classification report of type {%s} for recording {%s} called by user {%s} "
        "with filters min_prob={%s}, max_std={%s}", classification_type, recording_id,
        user.username, min_prob, max_std
    )

    recording = RecordingDataInDB(**_get_recording(id_=recording_id, username=user.username, db=db))

    if not recording.classification:
        raise NonExistingClassificationError()

    classification_info = recording.classification.get(classification_type.value)

    if not classification_info:
        raise NonExistingClassificationError()

    return _filter_classified_segments(segments=classification_info.segments,
                                       min_prob=min_prob,
                                       max_std=max_std)


@router.delete('/{recording_id}/report',
               responses={status.HTTP_400_BAD_REQUEST: {"model": ExceptionModel},
                          status.HTTP_401_UNAUTHORIZED: {"model": ExceptionModel},
                          status.HTTP_403_FORBIDDEN: {"model": ExceptionModel},
                          status.HTTP_404_NOT_FOUND: {"model": ExceptionModel}})
def delete_classification_report(recording_id: PyObjectId,
                                 classification_type: ClassificationType,
                                 user: UserInDB = Depends(get_current_user),
                                 db: Database = Depends(Database)):
    logger.debug("Delete classification report of type {%s} for recording {%s} called by user {%s}",
                 classification_type.value, recording_id, user.username)

    recording = RecordingDataInDB(**_get_recording(id_=recording_id, username=user.username, db=db))

    if recording.classification and recording.classification.get(classification_type.value):
        updated_recording = db.recordings_data.find_one_and_unset(
            id_=recording_id, username=user.username,
            unset_field=f'classification.{classification_type.value}'
        )
        if updated_recording:
            if not updated_recording.get('classification'):
                db.recordings_data.find_one_and_unset(
                    id_=recording_id, username=user.username, unset_field='classification')

            return str(updated_recording.get('_id'))
    else:
        raise NonExistingClassificationError()


def _filter_classified_segments(segments: List[ClassificationSegmentInDB],
                                min_prob: float,
                                max_std: Optional[float] = None) -> List[ClassificationSegmentInDB]:
    filtered_segments = [seg for seg in segments if seg.prob >= min_prob]
    if max_std:
        filtered_segments = [seg for seg in filtered_segments if seg.std <= max_std]

    return filtered_segments
