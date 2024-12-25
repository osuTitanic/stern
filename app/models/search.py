
from pydantic import BaseModel
from typing import Optional

from app.common.constants import (
    BeatmapCategory,
    BeatmapLanguage,
    BeatmapSortBy,
    BeatmapGenre,
    BeatmapOrder,
    GameMode
)

class SearchRequest(BaseModel):
    language: Optional[BeatmapLanguage] = None
    genre: Optional[BeatmapGenre] = None
    mode: Optional[GameMode] = None
    uncleared: Optional[bool] = None
    unplayed: Optional[bool] = None
    cleared: Optional[bool] = None
    played: Optional[bool] = None
    query: Optional[str] = None
    category: BeatmapCategory = BeatmapCategory.Leaderboard
    order: BeatmapOrder = BeatmapOrder.Descending
    sort: BeatmapSortBy = BeatmapSortBy.Ranked
    storyboard: bool = False
    video: bool = False
    titanic: bool = False
    page: int = 0
