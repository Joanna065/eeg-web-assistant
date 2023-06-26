import gzip
from collections import OrderedDict
from datetime import datetime

import gridfs
import mne
import pymongo
from pymongo import MongoClient

from eeg_web_assistant import settings
from eeg_web_assistant.utils.security import get_password_hash

client = MongoClient()

# CREATE DATABASE
db = client['eeg_assistant']

# DROP 'USER' IF EXISTS
if 'user' in db.list_collection_names():
    db.drop_collection('user')

# CREATE 'USER' COLLECTION
users = db['user']
user_vexpr = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["first_name", "last_name", "username", "password", "email"],
        "properties": {
            "first_name": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "last_name": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "email": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "username": {
                "bsonType": "string",
                "description": "must be an unique string"
            },
            "password": {
                "bsonType": "string",
                "description": "must be a string and is required"
            }
        }
    }
}
users.create_index("username", unique=True)
users.create_index("email", unique=True)

user_cmd = OrderedDict([('collMod', 'user'),
                        ('validator', user_vexpr),
                        ('validationLevel', 'moderate')])
db.command(user_cmd)

user_list = [
    {"first_name": "Jan",
     "last_name": "Kowalski",
     "email": "kowalski.jan@gmail.com",
     "username": "jan_k",
     "password": get_password_hash("jankowalski")},

    {"first_name": "Alicja",
     "last_name": "Nowak",
     "email": "nowak.alicja@gmail.com",
     "username": "alicja_n",
     "password": get_password_hash("alicjanowak")},

    {"first_name": "Maria",
     "last_name": "Krężel",
     "email": "krezel.maria@gmail.com",
     "username": "maria_k",
     "password": get_password_hash("mariakrezel")}
]

result = users.insert_many(user_list)
user_1, user_2, user_3 = 'jan_k', 'alicja_n', 'maria_k'

# DROP 'EDF_RECORDING_DATA' IF EXISTS
if 'edf_recording_data' in db.list_collection_names():
    db.drop_collection('edf_recording_data')

# CREATE 'EDF_RECORDING_DATA' COLLECTION
edf_recordings = db['edf_recording_data']
edf_vexpr = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["recording_info", "name", "raw_id", "username", "created"],
        "properties": {
            "recording_info": {
                "bsonType": "object",
                "required": ["ch_names", "sfreq", "n_times"],
                "properties": {
                    "ch_names": {"bsonType": "array"},
                    "sfreq": {"bsonType": "double"},
                    "n_times": {"bsonType": "int"},
                    "lowpass": {"bsonType": "double"},
                    "highpass": {"bsonType": "double"},
                    "meas_date": {"bsonType": "date"}
                }
            },
            "subject_info": {
                "bsonType": "object",
                "properties": {
                    "last_name": {"bsonType": "string"},
                    "first_name": {"bsonType": "string"},
                    "middle_name": {"bsonType": "string"},
                    "birthday": {"bsonType": "date"},
                    "sex": {"bsonType": "int"},
                    "hand": {"bsonType": "int"}
                }
            },
            "name": {"bsonType": "string"},
            "notes": {"bsonType": "string"},
            "raw_id": {"bsonType": "objectId"},
            "username": {"bsonType": "string"},
            "created": {"bsonType": "date"},
            "classification": {"bsonType": "object"}
        }
    }
}
edf_recordings.create_index("subject_info.last_name")
edf_recordings.create_index("subject_info.first_name")
edf_recordings.create_index("name")
edf_recordings.create_index("username")
edf_recordings.create_index([("created", pymongo.DESCENDING)])
edf_recordings.create_index("raw_id")

recording_cmd = OrderedDict([('collMod', 'edf_recording_data'),
                             ('validator', edf_vexpr),
                             ('validationLevel', 'moderate')])
db.command(recording_cmd)

# DROP 'EDF_RAW' gridFS COLLECTIONS IF EXIST
if 'edf_raw.files' in db.list_collection_names():
    db.drop_collection('edf_raw.files')

if 'edf_raw.chunks' in db.list_collection_names():
    db.drop_collection('edf_raw.chunks')

# CREATE 'EDF_RAW' gridFS COLLECTIONS
edf_raw = gridfs.GridFS(db, collection='edf_raw')

# INSERT EDF RECORDINGS
EXCLUDES_CHANNELS = ["BURSTS", "ECG EKG-REF", "EMG-REF", "IBI", "PHOTIC-REF", "PULSE RATE",
                     "RESP ABDOMEN-RE", "SUPPR"]

SEIZURE_1 = settings.DB_SAMPLES_DIR / 'seizure_1.edf'
SEIZURE_2 = settings.DB_SAMPLES_DIR / 'seizure_2.edf'
SEIZURE_3 = settings.DB_SAMPLES_DIR / 'seizure_3.edf'

seizure_1 = mne.io.read_raw_edf(str(SEIZURE_1), exclude=EXCLUDES_CHANNELS)
seizure_1.close()
seizure_2 = mne.io.read_raw_edf(str(SEIZURE_2), exclude=EXCLUDES_CHANNELS)
seizure_2.close()
seizure_3 = mne.io.read_raw_edf(str(SEIZURE_3), exclude=EXCLUDES_CHANNELS)
seizure_3.close()

with SEIZURE_1.open(mode='rb') as f:
    raw_bytes = f.read()
    seizure_raw_1 = edf_raw.put(gzip.compress(raw_bytes))

with SEIZURE_2.open(mode='rb') as f:
    raw_bytes = f.read()
    seizure_raw_2 = edf_raw.put(gzip.compress(raw_bytes))

with SEIZURE_3.open(mode='rb') as f:
    raw_bytes = f.read()
    seizure_raw_3 = edf_raw.put(gzip.compress(raw_bytes))

ARTIFACT_1 = settings.DB_SAMPLES_DIR / 'artifact_1.edf'
ARTIFACT_2 = settings.DB_SAMPLES_DIR / 'artifact_2.edf'
ARTIFACT_3 = settings.DB_SAMPLES_DIR / 'artifact_3.edf'
ARTIFACT_4 = settings.DB_SAMPLES_DIR / 'artifact_4.edf'

artifact_1 = mne.io.read_raw_edf(str(ARTIFACT_1), exclude=EXCLUDES_CHANNELS)
artifact_1.close()
artifact_2 = mne.io.read_raw_edf(str(ARTIFACT_2), exclude=EXCLUDES_CHANNELS)
artifact_2.close()
artifact_3 = mne.io.read_raw_edf(str(ARTIFACT_3), exclude=EXCLUDES_CHANNELS)
artifact_3.close()
artifact_4 = mne.io.read_raw_edf(str(ARTIFACT_4), exclude=EXCLUDES_CHANNELS)
artifact_4.close()

with ARTIFACT_1.open(mode='rb') as f:
    raw_bytes = f.read()
    artifact_raw_1 = edf_raw.put(gzip.compress(raw_bytes))

with ARTIFACT_2.open(mode='rb') as f:
    raw_bytes = f.read()
    artifact_raw_2 = edf_raw.put(gzip.compress(raw_bytes))

with ARTIFACT_3.open(mode='rb') as f:
    raw_bytes = f.read()
    artifact_raw_3 = edf_raw.put(gzip.compress(raw_bytes))

with ARTIFACT_4.open(mode='rb') as f:
    raw_bytes = f.read()
    artifact_raw_4 = edf_raw.put(gzip.compress(raw_bytes))

ABNORMAL_1 = settings.DB_SAMPLES_DIR / 'abnormal_1.edf'
ABNORMAL_2 = settings.DB_SAMPLES_DIR / 'abnormal_2.edf'

abnormal_1 = mne.io.read_raw_edf(str(ABNORMAL_1), exclude=EXCLUDES_CHANNELS)
abnormal_1.close()
abnormal_2 = mne.io.read_raw_edf(str(ABNORMAL_2), exclude=EXCLUDES_CHANNELS)
abnormal_2.close()

with ABNORMAL_1.open(mode='rb') as f:
    raw_bytes = f.read()
    abnormal_raw_1 = edf_raw.put(gzip.compress(raw_bytes))

with ABNORMAL_2.open(mode='rb') as f:
    raw_bytes = f.read()
    abnormal_raw_2 = edf_raw.put(gzip.compress(raw_bytes))

recordings = [
    {
        "recording_info": {
            "meas_date": seizure_1.info.get('meas_date'),
            "ch_names": seizure_1.ch_names,
            "lowpass": seizure_1.info.get('lowpass'),
            "highpass": seizure_1.info.get('highpass'),
            "sfreq": seizure_1.info.get('sfreq'),
            "n_times": seizure_1.n_times.item()
        },
        "subject_info": {
            "first_name": "Jan",
            "last_name": "Nowak",
            "middle_name": "Przemysław",
            "birthday": datetime(1985, 8, 15),
            "sex": 1,
            "hand": 2
        },
        "name": "Seizure recording nr 1",
        "notes": "Seizure parts of GNSZ type (Generalized Non-Specific Seizure)",
        "created": datetime.utcnow(),
        "username": user_1,
        "raw_id": seizure_raw_1
    },
    {
        "recording_info": {
            "meas_date": seizure_2.info.get('meas_date'),
            "ch_names": seizure_2.ch_names,
            "lowpass": seizure_2.info.get('lowpass'),
            "highpass": seizure_2.info.get('highpass'),
            "sfreq": seizure_2.info.get('sfreq'),
            "n_times": seizure_2.n_times.item()
        },
        "subject_info": {
            "first_name": "Maria",
            "last_name": "Halfar",
            "middle_name": "Gabriela",
            "birthday": datetime(1997, 12, 10),
            "sex": 2,
            "hand": 3
        },
        "name": "Seizure recording nr 2",
        "notes": "Seizure parts of GNSZ type (Generalized Non-Specific Seizure)",
        "created": datetime.utcnow(),
        "username": user_1,
        "raw_id": seizure_raw_2
    },
    {
        "recording_info": {
            "meas_date": seizure_3.info.get('meas_date'),
            "ch_names": seizure_3.ch_names,
            "lowpass": seizure_3.info.get('lowpass'),
            "highpass": seizure_3.info.get('highpass'),
            "sfreq": seizure_3.info.get('sfreq'),
            "n_times": seizure_3.n_times.item()
        },
        "name": "Seizure recording nr 3",
        "notes": "Seizure parts of GNSZ type (Generalized Non-Specific Seizure)",
        "created": datetime.utcnow(),
        "username": user_1,
        "raw_id": seizure_raw_3
    },
    {
        "recording_info": {
            "meas_date": artifact_1.info.get('meas_date'),
            "ch_names": artifact_1.ch_names,
            "lowpass": artifact_1.info.get('lowpass'),
            "highpass": artifact_1.info.get('highpass'),
            "sfreq": artifact_1.info.get('sfreq'),
            "n_times": artifact_1.n_times.item()
        },
        "subject_info": {
            "first_name": "Piotr",
            "last_name": "Gacka",
            "middle_name": "Jerzy",
            "birthday": datetime(1965, 3, 17),
            "sex": 1,
            "hand": 2
        },
        "name": "Artifact recording nr 1",
        "notes": "Artifacts: eye movement, elpp",
        "created": datetime.utcnow(),
        "username": user_2,
        "raw_id": artifact_raw_1
    },
    {
        "recording_info": {
            "meas_date": artifact_2.info.get('meas_date'),
            "ch_names": artifact_2.ch_names,
            "lowpass": artifact_2.info.get('lowpass'),
            "highpass": artifact_2.info.get('highpass'),
            "sfreq": artifact_2.info.get('sfreq'),
            "n_times": artifact_2.n_times.item()
        },
        "name": "Artifact recording nr 2",
        "created": datetime.utcnow(),
        "notes": "Artifacts: musc",
        "username": user_2,
        "raw_id": artifact_raw_2
    },
    {
        "recording_info": {
            "meas_date": artifact_3.info.get('meas_date'),
            "ch_names": artifact_3.ch_names,
            "lowpass": artifact_3.info.get('lowpass'),
            "highpass": artifact_3.info.get('highpass'),
            "sfreq": artifact_3.info.get('sfreq'),
            "n_times": artifact_3.n_times.item()
        },
        "name": "Artifact recording nr 3",
        "notes": "Artifacts: eye movement",
        "created": datetime.utcnow(),
        "username": user_2,
        "raw_id": artifact_raw_3
    },
    {
        "recording_info": {
            "meas_date": artifact_4.info.get('meas_date'),
            "ch_names": artifact_4.ch_names,
            "lowpass": artifact_4.info.get('lowpass'),
            "highpass": artifact_4.info.get('highpass'),
            "sfreq": artifact_4.info.get('sfreq'),
            "n_times": artifact_4.n_times.item()
        },
        "subject_info": {
            "first_name": "Łukasz",
            "last_name": "Młynarczyk",
            "middle_name": "Paweł",
            "birthday": datetime(1995, 2, 6),
            "sex": 1,
            "hand": 1
        },
        "name": "Artifact recording nr 4",
        "notes": "Artifacts: eye movement",
        "created": datetime.utcnow(),
        "username": user_2,
        "raw_id": artifact_raw_4
    },
    {
        "recording_info": {
            "meas_date": abnormal_1.info.get('meas_date'),
            "ch_names": abnormal_1.ch_names,
            "lowpass": abnormal_1.info.get('lowpass'),
            "highpass": abnormal_1.info.get('highpass'),
            "sfreq": abnormal_1.info.get('sfreq'),
            "n_times": abnormal_1.n_times.item()
        },
        "subject_info": {
            "first_name": "Natalia",
            "last_name": "Kałuża",
            "middle_name": "Janina",
            "birthday": datetime(1990, 7, 5),
            "sex": 2,
            "hand": 1
        },
        "name": "Abnormal recording nr 1",
        "notes": "Frequent left posterior quadrant/occipital sharp waves with after-going slow "
                 "waves. Intermittent mild, at times rhythmic, focal left posterior quadrant "
                 "slowing. Stage 2 sleep.",
        "created": datetime.utcnow(),
        "username": user_3,
        "raw_id": abnormal_raw_1
    },
    {
        "recording_info": {
            "meas_date": abnormal_2.info.get('meas_date'),
            "ch_names": abnormal_2.ch_names,
            "lowpass": abnormal_2.info.get('lowpass'),
            "highpass": abnormal_2.info.get('highpass'),
            "sfreq": abnormal_2.info.get('sfreq'),
            "n_times": abnormal_2.n_times.item()
        },
        "subject_info": {
            "first_name": "Agnieszka",
            "last_name": "Dziak",
            "middle_name": "Patrycja",
            "birthday": datetime(1959, 10, 25),
            "sex": 2,
            "hand": 1
        },
        "name": "Abnormal recording nr 2",
        "notes": "Generalized slowing of background activity and slowing of the posterior dominant "
                 "rhythm during wakefulness, most pronounced on the right side. Breach rhythm "
                 "in the right posterior quadrant region. Intermittent polymorphic delta and theta "
                 "activity at times with sharply contoured features in frontotemporal regions "
                 "bilaterally. Occasional sharp waves seen arising from the right temporal region "
                 "and rarely from left temporal region.",
        "created": datetime.utcnow(),
        "username": user_3,
        "raw_id": abnormal_raw_2
    }
]

edf_recordings.insert_many(recordings)
