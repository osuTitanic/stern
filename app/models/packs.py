
from __future__ import annotations

from pydantic import BaseModel
from datetime import datetime
from typing import List

from .user import UserModel
from .beatmapset import BeatmapsetModel

class BeatmapPackEntryModel(BaseModel):
    beatmapset: BeatmapsetModel
    created_at: datetime

class BeatmapPackModel(BaseModel):
    id: int
    name: str
    category: str
    description: str
    download_link: str
    creator: UserModel
    created_at: datetime
    updated_at: datetime

class BeatmapPackWithEntriesModel(BaseModel):
    id: int
    name: str
    category: str
    description: str
    download_link: str
    creator: UserModel
    created_at: datetime
    updated_at: datetime
    entries: List[BeatmapPackEntryModel]
