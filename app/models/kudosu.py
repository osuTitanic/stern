
from pydantic import BaseModel
from datetime import datetime

from .beatmapset import BeatmapsetModel
from .forums import PostModel
from .user import UserModel

class KudosuModel(BaseModel):
    id: int
    target: UserModel
    sender: UserModel
    beatmapset: BeatmapsetModel
    post: PostModel
    amount: int
    time: datetime
