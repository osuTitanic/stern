from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from .user import UserModel

class BenchmarkModel(BaseModel):
    id: int
    smoothness: float
    framerate: int
    score: int
    grade: str
    created_at: datetime
    client: str
    hardware: Optional[dict]
    user: UserModel
