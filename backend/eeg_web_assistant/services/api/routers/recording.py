import pathlib
from datetime import datetime
from math import ceil, floor
from tempfile import NamedTemporaryFile
from typing import Dict, List, Optional

import fastapi
import numpy as np
from bson import ObjectId
from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from pydantic import constr

from eeg_web_assistant import settings
from eeg_web_assistant.core.edf_file import EdfFile
from eeg_web_assistant.models.plot import RecordingPlot
from eeg_web_assistant.models.recording import (RecordingDataInDB, RecordingDataListItemOut,
                                                RecordingDataOut, RecordingInfoInDB, SortByQuery,
                                                UpdateRecordingData, UpdateSubjectInfo)
from eeg_web_assistant.models.user import UserInDB
from eeg_web_assistant.services.database import Database
from eeg_web_assistant.services.logging import Logging
from eeg_web_assistant.utils.bson import PyObjectId
from eeg_web_assistant.utils.dict import get_dict_with_prefix_keys
from eeg_web_assistant.utils.exceptions import (EdfDurationExceededError, EdfExtensionError,
                                                EdfReadError, ExceptionModel,
                                                PlotFragmentNrExceededError,
                                                RecordingForbiddenAccessError,
                                                RecordingNotFoundError)
from eeg_web_assistant.utils.security import get_current_user

logger = Logging.get(__name__)

router = APIRouter()


@router.get('/all',
            response_model=List[RecordingDataListItemOut],
            responses={status.HTTP_401_UNAUTHORIZED: {'model': ExceptionModel}})
def get_all_recordings(user: UserInDB = Depends(get_current_user),
                       filter_text: Optional[constr(max_length=50)] = Query(None),
                       sort_by: Optional[SortByQuery] = Query(SortByQuery.DATE_DESC),
                       db: Database = Depends(Database)):
    logger.debug(
        "Get all recordings called with query params: filter={%s}, sort_by={%s} by user {%s}",
        filter_text, sort_by, user.username
    )

    recordings = db.recordings_data.find_many_by_username_and_sort(username=user.username,
                                                                   sort_by=sort_by.name)
    recordings = [RecordingDataInDB(**rec) for rec in recordings]

    recordings_out = []
    for rec in recordings:
        subject_full_name = None
        if rec.subject_info:
            subject_full_name = f'{rec.subject_info.last_name} {rec.subject_info.first_name}'

        rec_out = RecordingDataListItemOut(_id=rec.id, subject_full_name=subject_full_name,
                                           name=rec.name, created=rec.created)
        recordings_out.append(rec_out)

    if filter_text:
        filter_text = filter_text.lower().strip()
        recordings_filtered = []

        for rec in recordings_out:
            if (filter_text in rec.name.lower()
                    or rec.subject_full_name and filter_text in rec.subject_full_name.lower()):
                recordings_filtered.append(rec)

        recordings_out = recordings_filtered

    return recordings_out


@router.get('/{id_}',
            response_model=RecordingDataOut,
            response_model_exclude_unset=True,
            responses={status.HTTP_401_UNAUTHORIZED: {'model': ExceptionModel},
                       status.HTTP_403_FORBIDDEN: {'model': ExceptionModel},
                       status.HTTP_404_NOT_FOUND: {'model': ExceptionModel}})
def get_recording(id_: PyObjectId, user: UserInDB = Depends(get_current_user),
                  db: Database = Depends(Database)):
    logger.debug("Get recording data with id {%s} called by user {%s}", id_, user.username)

    return _get_recording(id_=id_, username=user.username, db=db)


@router.delete('/{id_}',
               responses={status.HTTP_401_UNAUTHORIZED: {'model': ExceptionModel},
                          status.HTTP_403_FORBIDDEN: {'model': ExceptionModel},
                          status.HTTP_404_NOT_FOUND: {'model': ExceptionModel}})
def delete_recording(id_: PyObjectId, user: UserInDB = Depends(get_current_user),
                     db: Database = Depends(Database)):
    logger.debug("Delete recording with id {%s} called by user {%s}", id_, user.username)

    recording_by_id = db.recordings_data.find_one_by_id(id_=id_)
    if not recording_by_id:
        raise RecordingNotFoundError()

    deleted_recording = db.recordings_data.find_one_and_delete(id_=id_, username=user.username)
    if deleted_recording:
        db.recordings_raw.delete(deleted_recording.get('raw_id'))
    else:
        raise RecordingForbiddenAccessError()

    return str(deleted_recording.get('_id'))


@router.post('',
             responses={status.HTTP_400_BAD_REQUEST: {'model': ExceptionModel},
                        status.HTTP_401_UNAUTHORIZED: {'model': ExceptionModel}})
def create_recording(name: constr(max_length=30), new_file: UploadFile = File(...),
                     user: UserInDB = Depends(get_current_user),
                     db: Database = Depends(Database)):
    logger.debug("Create recording called by user {%s}", user.username)

    if not new_file.filename.endswith('.edf'):
        raise EdfExtensionError()

    edf_raw_bytes = new_file.file.read()
    new_file.file.close()

    with NamedTemporaryFile(suffix='.edf') as tf:
        tf.write(edf_raw_bytes)
        try:
            edf_file = EdfFile(path=pathlib.Path(tf.name))
        except ValueError:
            raise EdfReadError()

    if ceil(edf_file.duration / 60) > settings.EdfFileConfig.MAX_DURATION_MINUTES:
        raise EdfDurationExceededError()

    inserted_raw_id = db.recordings_raw.put(edf_raw_bytes)

    record_info = RecordingInfoInDB(meas_date=edf_file.measure_date, highpass=edf_file.highpass,
                                    lowpass=edf_file.lowpass, sfreq=edf_file.sampling_frequency,
                                    n_times=edf_file.n_times, ch_names=edf_file.channel_names)

    new_recording = RecordingDataInDB(name=name,
                                      username=user.username,
                                      created=datetime.utcnow(),
                                      recording_info=record_info.dict(exclude_unset=True),
                                      raw_id=inserted_raw_id)

    if edf_file.subject_info:
        new_recording.subject_info = edf_file.subject_info

    inserted_id = db.recordings_data.insert_one(new_recording.dict(exclude_unset=True))

    return inserted_id


@router.patch('/{id_}',
              responses={status.HTTP_401_UNAUTHORIZED: {'model': ExceptionModel},
                         status.HTTP_403_FORBIDDEN: {'model': ExceptionModel}})
def update_recording(id_: PyObjectId,
                     updated_recording: UpdateRecordingData,
                     user: UserInDB = Depends(get_current_user),
                     db: Database = Depends(Database)):
    logger.debug("Update recording data called by user {%s} with update data {%s}",
                 user.username, updated_recording.dict(exclude_unset=True))

    if updated_recording.dict(exclude_unset=True, exclude_none=True):
        _get_recording(id_=id_, username=user.username, db=db)

        updated_recording = db.recordings_data.find_one_by_id_and_username_and_update(
            id_=id_,
            username=user.username,
            update_data=updated_recording.dict(exclude_unset=True, exclude_none=True)
        )

        if updated_recording:
            return str(updated_recording.get('_id'))


@router.patch('/{id_}/subject_info',
              responses={status.HTTP_401_UNAUTHORIZED: {'model': ExceptionModel},
                         status.HTTP_403_FORBIDDEN: {'model': ExceptionModel},
                         status.HTTP_404_NOT_FOUND: {'model': ExceptionModel}})
def update_recording_subject_info(id_: PyObjectId,
                                  updated_subject: UpdateSubjectInfo,
                                  user: UserInDB = Depends(get_current_user),
                                  db: Database = Depends(Database)):
    logger.debug("Update recording subject called by user {%s} with update data {%s}",
                 user.username, updated_subject.dict(exclude_unset=True, exclude_none=True))

    _get_recording(id_=id_, username=user.username, db=db)

    updated_recording = db.recordings_data.find_one_by_id_and_username_and_update(
        id_=id_,
        username=user.username,
        update_data=get_dict_with_prefix_keys(
            dictionary=updated_subject.dict(exclude_unset=True, exclude_none=True),
            prefix='subject_info.'
        )
    )

    if updated_recording:
        return str(updated_recording.get('_id'))


@router.get('/{id_}/plot/{nr}',
            response_model=RecordingPlot,
            responses={status.HTTP_400_BAD_REQUEST: {'model': ExceptionModel},
                       status.HTTP_401_UNAUTHORIZED: {'model': ExceptionModel},
                       status.HTTP_403_FORBIDDEN: {'model': ExceptionModel},
                       status.HTTP_404_NOT_FOUND: {'model': ExceptionModel}})
def get_plot_data(id_: PyObjectId,
                  nr: int = fastapi.Path(..., ge=0, title='Number of plot fragment to get'),
                  user: UserInDB = Depends(get_current_user),
                  db: Database = Depends(Database)):
    logger.debug("Get plot data called by user {%s} for recording id={%s}, plot_nr={%s}",
                 user.username, id_, nr)

    recording = RecordingDataInDB(**_get_recording(id_=id_, username=user.username, db=db))
    rec_duration_seconds = recording.recording_info.n_times // recording.recording_info.sfreq

    max_fragment_nr = floor(rec_duration_seconds / settings.PlotConfig.FRAGMENT_DURATION_SECONDS)
    if nr > max_fragment_nr:
        raise PlotFragmentNrExceededError()

    raw_data = db.recordings_raw.get(recording.raw_id)

    with NamedTemporaryFile(suffix='.edf') as tf:
        tf.write(raw_data)

        edf_file = EdfFile(path=pathlib.Path(tf.name))
        if edf_file.sampling_frequency > settings.PlotConfig.MAX_SAMPLING_FREQUENCY:
            edf_file.resample(new_sfreq=settings.PlotConfig.MAX_SAMPLING_FREQUENCY)

        edf_numpy = edf_file.to_numpy()

    step = int(settings.PlotConfig.FRAGMENT_DURATION_SECONDS * edf_file.sampling_frequency)
    begin_idx = int(nr * step)
    end_idx = begin_idx + step

    fragment_array = edf_numpy[:, begin_idx:end_idx]
    fragment_array = fragment_array.astype(np.float16)

    return RecordingPlot(ch_names=edf_file.channel_names,
                         data_array=fragment_array.tolist(),
                         sfreq=edf_file.sampling_frequency)


def _get_recording(id_: ObjectId, username: str, db: Database) -> Dict:
    recording_by_id = db.recordings_data.find_one_by_id(id_=id_)

    if not recording_by_id:
        raise RecordingNotFoundError()

    recording_by_id_and_username = db.recordings_data.find_one_by_id_and_username(id_=id_,
                                                                                  username=username)

    if not recording_by_id_and_username:
        raise RecordingForbiddenAccessError()

    return recording_by_id_and_username
