
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

from app.common.database import DBRating, DBFavourite

class _BeatmapModel(BaseModel):
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

class BeatmapsetModel(BaseModel):
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
    ratings: list
    favourites: list
    beatmaps: List[_BeatmapModel]

    @validator('ratings')
    def avg_rating(cls, ratings: List[DBRating]) -> float:
        if not ratings:
            return 0.0

        ratings = [r.rating for r in ratings]

        return sum(ratings) / len(ratings)

    @validator('favourites')
    def sum_favourites(cls, favourites: List[DBFavourite]) -> int:
        return len(favourites)
