
from flask import Blueprint, request
from flask_pydantic import validate
from typing import List

from app.common.database.repositories import plays
from app.models import BeatmapModel

router = Blueprint("history", __name__)

@router.get('/<user_id>/history/plays')
@validate()
def most_played(user_id: int) -> List[dict]:
    offset = request.args.get('offset', default=0, type=int)
    limit = max(1, min(50, request.args.get('limit', default=15, type=int)))

    most_played = plays.fetch_most_played_by_user(user_id, limit, offset)

    return [
        {
            'count': plays.count,
            'beatmap': BeatmapModel.model_validate(
                plays.beatmap,
                from_attributes=True
            ).model_dump()
        }
        for plays in most_played
    ]
