from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, constr

from eeg_web_assistant.core.classification_types import ClassificationType
from eeg_web_assistant.models.base import DatabaseModel
from eeg_web_assistant.utils.bson import PyObjectId


# models to database insertion
class SubjectInfoInDB(BaseModel):
    first_name: str
    middle_name: Optional[str]
    last_name: str
    birthday: Optional[datetime]
    sex: Optional[int]
    hand: Optional[int]


class RecordingInfoInDB(BaseModel):
    meas_date: Optional[datetime]
    highpass: Optional[float]
    lowpass: Optional[float]
    n_times: int
    sfreq: float
    ch_names: List[str]


class ClassificationSegmentInDB(BaseModel):
    nr: int
    prob: float
    std: float
    start_time: int
    stop_time: int


class ClassificationInfoInDB(BaseModel):
    type: ClassificationType
    segments: List[ClassificationSegmentInDB]

    class Config:
        use_enum_values = True
        json_encoders = {
            ClassificationType: lambda type: type.value
        }
        schema_extra = {
            'example': {
                'type': ClassificationType.SEIZURE,
                'segments': [{'nr': 0,
                              'prob': 0.95,
                              'std': 0.006,
                              'start_time': 0,
                              'stop_time': 16},
                             {'nr': 1,
                              'prob': 0.55,
                              'std': 0.006,
                              'start_time': 16,
                              'stop_time': 32},
                             {'nr': 2,
                              'prob': 0.67,
                              'std': 0.01,
                              'start_time': 32,
                              'stop_time': 48}]
            }
        }


class RecordingDataInDB(DatabaseModel):
    name: str
    notes: Optional[str]
    username: str
    raw_id: PyObjectId
    created: datetime
    recording_info: RecordingInfoInDB
    subject_info: Optional[SubjectInfoInDB]
    classification: Optional[Dict[ClassificationType, ClassificationInfoInDB]]

    class Config:
        use_enum_values = True


# DTOs
class SortByQuery(Enum):
    DATE_ASC = 'date.asc'
    DATE_DESC = 'date.desc'
    SUBJECT_ASC = 'subject.asc'
    SUBJECT_DESC = 'subject.desc'


class RecordingDataOut(RecordingDataInDB):
    pass


class RecordingDataListItemOut(DatabaseModel):
    name: str
    created: datetime
    subject_full_name: Optional[str]  # concatenated last_name and first_name

    class Config:
        extra = 'ignore'
        schema_extra = {
            'example': {
                'id': '5fa17e3b8db3a7b594ccfb92',
                'name': 'EEG recording',
                'created': '2020-11-03T15:58:51.532Z',
                'subject_full_name': 'Adam Nowak'
            }
        }


class UpdateRecordingData(BaseModel):
    name: Optional[constr(max_length=30)]
    notes: Optional[constr(max_length=500)]

    class Config:
        extra = 'forbid'
        schema_extra = {
            'example': {
                'name': 'Updated recording name',
                'notes': 'Notes to recording'
            }
        }


class HandEnum(Enum):
    RIGHT: int = 1
    LEFT: int = 2
    AMBIDEXTROUS: int = 3


class SexEnum(Enum):
    UNKNOWN: int = 0
    MALE: int = 1
    FEMALE: int = 2


class UpdateSubjectInfo(BaseModel):
    first_name: constr(max_length=255)
    middle_name: Optional[constr(max_length=255)]
    last_name: constr(max_length=255)
    birthday: Optional[datetime]
    sex: Optional[SexEnum]
    hand: Optional[HandEnum]

    class Config:
        extra = 'forbid'
        use_enum_values = True
        schema_extra = {
            'example': {
                'first_name': 'Emilia',
                'middle_name': 'Agnieszka',
                'last_name': 'Pleszewska',
                'birthday': datetime(1980, 7, 2),
                'sex': SexEnum['FEMALE'].value,
                'hand': HandEnum['RIGHT'].value
            }
        }
