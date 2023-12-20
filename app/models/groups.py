
from pydantic import BaseModel
from typing import Optional

class GroupModel(BaseModel):
    id: int
    name: str
    short_name: str
    description: Optional[str]
    color: str
    hidden: bool

class GroupEntryModel(BaseModel):
    user_id: int
    group_id: int
    group: GroupModel
