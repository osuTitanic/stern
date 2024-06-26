
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class _BeatmapsetModel(BaseModel):
    id: int
    title: Optional[str]
    artist: Optional[str]
    creator: Optional[str]
    source: Optional[str]
    tags: Optional[str]
    creator_id: Optional[int]
    status: int
    has_video: bool
    has_storyboard: bool
    server: int
    available: bool
    created_at: datetime
    approved_at: Optional[datetime]
    last_update: datetime
    osz_filesize: int
    osz_filesize_novideo: int
    language_id: int
    genre_id: int

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
    beatmapset: _BeatmapsetModel
