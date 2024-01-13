
from __future__ import annotations

from pydantic import BaseModel
from datetime import datetime
from typing import List

from .user import UserModel

class MatchEventModel(BaseModel):
    time: datetime
    type: int
    data: dict

class MatchModel(BaseModel):
    id: int
    name: str
    created_at: datetime
    ended_at: datetime | None
    creator: UserModel
    events: List[MatchEventModel]
