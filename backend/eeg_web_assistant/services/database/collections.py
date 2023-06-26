import gzip
from abc import ABC
from enum import Enum
from typing import Dict, List, Optional

import gridfs
import pymongo
from bson import ObjectId
from pymongo import ReturnDocument


class BaseCollection(ABC):
    def __init__(self, database, collection):
        self._collection = database[collection]


class _UserCollection(BaseCollection):
    def find_one_by_username(self, username: str) -> Optional[Dict]:
        return self._collection.find_one(filter={'username': username})

    def find_one_by_email(self, email: str) -> Optional[Dict]:
        return self._collection.find_one(filter={'email': email})

    def insert_one(self, user: Dict) -> Optional[str]:
        inserted_user = self._collection.insert_one(user)
        if inserted_user:
            return str(inserted_user.inserted_id)

    def find_one_and_update(self, username: str, update_data: Dict) -> Optional[Dict]:
        return self._collection.find_one_and_update(filter={'username': username},
                                                    update={'$set': update_data},
                                                    return_document=ReturnDocument.AFTER)

    def find_one_and_delete(self, username: str) -> Optional[Dict]:
        return self._collection.find_one_and_delete(filter={'username': username})


class _RecordingDataCollection(BaseCollection):
    class SortByInDB(Enum):
        DATE_ASC = [('created', pymongo.ASCENDING)]
        DATE_DESC = [('created', pymongo.DESCENDING)]
        SUBJECT_ASC = [('subject_info.last_name', pymongo.ASCENDING),
                       ('subject_info.first_name', pymongo.ASCENDING)]
        SUBJECT_DESC = [('subject_info.last_name', pymongo.DESCENDING),
                        ('subject_info.first_name', pymongo.DESCENDING)]

    def find_many_by_username_and_sort(self, username: str, sort_by: str) -> List[Dict]:
        return list(self._collection
                    .find(filter={'username': username})
                    .sort(self.SortByInDB[sort_by].value))

    def find_many_by_username_return_raw_ids(self, username: str) -> List[Dict]:
        return list(self._collection.find(filter={'username': username},
                                          projection={'username': True, 'raw_id': True}))

    def find_one_by_id(self, id_: ObjectId) -> Optional[Dict]:
        return self._collection.find_one(filter={'_id': id_})

    def find_one_by_id_and_username(self, id_: ObjectId, username: str) -> Optional[Dict]:
        return self._collection.find_one(filter={'_id': id_, 'username': username})

    def insert_one(self, recording: Dict) -> Optional[str]:
        inserted_obj = self._collection.insert_one(recording)
        if inserted_obj:
            return str(inserted_obj.inserted_id)

    def find_one_by_id_and_update(self, id_: ObjectId, update_data: Dict) -> Optional[Dict]:
        return self._collection.find_one_and_update(filter={'_id': id_},
                                                    update={'$set': update_data},
                                                    return_document=ReturnDocument.AFTER)

    def find_one_by_id_and_username_and_update(self,
                                               id_: ObjectId,
                                               username: str,
                                               update_data: Dict) -> Optional[Dict]:
        return self._collection.find_one_and_update(filter={'_id': id_, 'username': username},
                                                    update={'$set': update_data},
                                                    return_document=ReturnDocument.AFTER)

    def find_one_and_unset(self,
                           id_: ObjectId,
                           username: str,
                           unset_field: str) -> Optional[Dict]:
        return self._collection.find_one_and_update(filter={'_id': id_, 'username': username},
                                                    update={'$unset': {unset_field: ""}},
                                                    return_document=ReturnDocument.AFTER)

    def find_one_and_delete(self, id_: ObjectId, username: str) -> Optional[Dict]:
        return self._collection.find_one_and_delete(filter={'_id': id_, 'username': username})

    def find_many_and_delete(self, username: str):
        return self._collection.delete_many(filter={'username': username})


class _RecordingRawCollection(BaseCollection):
    def __init__(self, database, collection):
        super().__init__(database, collection)
        self._fs = gridfs.GridFS(database, collection=collection)

    def put(self, raw_data: bytes) -> ObjectId:
        raw_id = self._fs.put(gzip.compress(raw_data))

        return raw_id

    def get(self, file_id: ObjectId) -> bytes:
        raw_data = self._fs.get(file_id).read()

        return gzip.decompress(raw_data)

    def delete(self, file_id: ObjectId):
        self._fs.delete(file_id)
