
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from .groups import GroupEntryModel

class RelationshipModel(BaseModel):
    user_id: int
    target_id: int
    status: int

class AchievementModel(BaseModel):
    user_id: int
    name: str
    category: str
    filename: str
    unlocked_at: datetime

class FavouritesModel(BaseModel):
    user_id: int
    set_id: int
    created_at: datetime

class BadgeModel(BaseModel):
    id: int
    user_id: int
    created: datetime
    badge_icon: str
    badge_url: Optional[str]
    badge_description: Optional[str]

class NameHistoryModel(BaseModel):
    id: int
    user_id: int
    changed_at: datetime
    name: str

class StatsModel(BaseModel):
    mode: int
    rank: int
    tscore: int
    rscore: int
    pp: float
    ppv1: float
    playcount: int
    playtime: int
    acc: float
    max_combo: int
    total_hits: int
    replay_views: int
    xh_count: int
    x_count: int
    sh_count: int
    s_count: int
    a_count: int
    b_count: int
    c_count: int
    d_count: int

class UserModel(BaseModel):
    id: int
    name: str
    country: str
    created_at: datetime
    latest_activity: datetime
    silence_end: Optional[datetime]
    restricted: bool
    activated: bool
    preferred_mode: int
    playstyle: int
    userpage: Optional[str]
    signature: Optional[str]
    banner: Optional[str]
    website: Optional[str]
    discord: Optional[str]
    twitter: Optional[str]
    location: Optional[str]
    interests: Optional[str]

    relationships: List[RelationshipModel]
    achievements: List[AchievementModel]
    names: List[NameHistoryModel]
    badges: List[BadgeModel]
    stats: List[StatsModel]
    groups: List[GroupEntryModel]
