from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from eeg_web_assistant.utils.bson import PyObjectId


class DatabaseModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: lambda _id: str(_id)
        }
