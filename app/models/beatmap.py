
from pydantic import BaseModel
from datetime import datetime

from .beatmapset import BeatmapsetModel

class BeatmapModel(BaseModel):
    id: int
    set_id: int
    mode: int
    md5: str
    status: int
    version: str
    filename: str
    created_at: datetime
    last_update: datetime
    playcount: int
    passcount: int
    total_length: int
    max_combo: int
    bpm: float
    cs: float
    ar: float
    od: float
    hp: float
    diff: float
    beatmapset: BeatmapsetModel
