
from pydantic import BaseModel
from datetime import datetime

class RankHistoryModel(BaseModel):
    time: datetime
    mode: int
    rscore: int
    pp: int
    global_rank: int
    country_rank: int
    score_rank: int

class PlaysHistoryModel(BaseModel):
    year: int
    month: int
    mode: int
    plays: int
