
from pydantic import BaseModel
from typing import Optional

from app.common.constants import (
    BeatmapLanguage,
    BeatmapSortBy,
    BeatmapGenre,
    GameMode
)

class SearchRequest(BaseModel):
    language: Optional[BeatmapLanguage] = None
    genre: Optional[BeatmapGenre] = None
    mode: Optional[GameMode] = None
    played: Optional[bool] = None
    query: Optional[str] = None
    sort: BeatmapSortBy = BeatmapSortBy.Plays
    status: Optional[int] = None
    has_storyboard: bool = False
    has_video: bool = False
    offset: int = 0
    limit: int = 40
