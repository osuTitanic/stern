
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

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
    userpage_about: Optional[str]
    userpage_signature: Optional[str]
    userpage_banner: Optional[str]
    userpage_website: Optional[str]
    userpage_discord: Optional[str]
    userpage_twitter: Optional[str]
    userpage_location: Optional[str]
    userpage_interests: Optional[str]

    # TODO: Stats
    # TODO: Friends
    # TODO: ...
