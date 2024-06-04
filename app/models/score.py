
from pydantic import BaseModel
from datetime import datetime

from .beatmap import BeatmapModel
from .user import UserModel

class ScoreModel(BaseModel):
    id: int
    user_id: int
    submitted_at: datetime
    mode: int
    status: int
    client_version: int
    pp: float
    acc: float
    total_score: int
    max_combo: int
    mods: int
    perfect: bool
    n300: int
    n100: int
    n50: int
    nMiss: int
    nGeki: int
    nKatu: int
    grade: str
    pinned: bool
    beatmap: BeatmapModel
    user: UserModel
