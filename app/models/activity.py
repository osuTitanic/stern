
from pydantic import BaseModel
from datetime import datetime

class ActivityModel(BaseModel):
    id: int
    user_id: int
    mode: int
    time: datetime
    activity: str
