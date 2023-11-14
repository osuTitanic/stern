
from flask import Blueprint, Response, request
from typing import List

from app.common.database.repositories import plays, users
from app.models import BeatmapModel

router = Blueprint("plays", __name__)

@router.get('/<user_id>/plays')
def most_played(user_id: str) -> List[dict]:
    if not user_id.isdigit():
        # Lookup user by username
        if not (user := users.fetch_by_name_extended(user_id)):
            return Response(
                response=(),
                status=404,
                mimetype='application/json'
            )

        user_id = user.id

    offset = request.args.get('offset', default=0, type=int)
    limit = max(1, min(50, request.args.get('limit', default=15, type=int)))

    most_played = plays.fetch_most_played_by_user(int(user_id), limit, offset)

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
