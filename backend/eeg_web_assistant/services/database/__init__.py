from pymongo import MongoClient

from eeg_web_assistant import settings
from eeg_web_assistant.services import Service
from eeg_web_assistant.services.database.collections import (_RecordingDataCollection,
                                                             _RecordingRawCollection,
                                                             _UserCollection)


class Database(metaclass=Service):
    def __init__(self, config: settings.DatabaseConfig):
        self.config = config

        self._client = MongoClient(self.config.ADDRESS)
        self._database = self._client[self.config.DB_NAME]

        self.users = _UserCollection(
            database=self._database,
            collection=self.config.USER_COLLECTION)

        self.recordings_data = _RecordingDataCollection(
            database=self._database,
            collection=self.config.RECORDING_DATA_COLLECTION)

        self.recordings_raw = _RecordingRawCollection(
            database=self._database,
            collection=self.config.RECORDING_RAW_COLLECTION)
