
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BeatmapsetModel(BaseModel):
    id: int
    title: Optional[str]
    artist: Optional[str]
    creator: Optional[str]
    source: Optional[str]
    tags: Optional[str]
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
