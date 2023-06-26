from typing import List

from pydantic import BaseModel


class RecordingPlot(BaseModel):
    ch_names: List[str]
    data_array: List[List[float]]
    sfreq: float
