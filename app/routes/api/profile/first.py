
from flask import Blueprint, abort, request
from typing import List

from app.common.database.repositories import scores
from app.common.constants import GameMode
from app.models import ScoreModel

router = Blueprint("first", __name__)

@router.get('/<user_id>/first/<mode>')
def leader_scores(
    user_id: int,
    mode: str
) -> List[dict]:
    if (mode := GameMode.from_alias(mode)) is None:
        return abort(400)

    offset = request.args.get('offset', default=0, type=int)
    limit = max(1, min(50, request.args.get('limit', default=50, type=int)))

    top_plays = scores.fetch_leader_scores(
        user_id,
        mode,
        offset=offset,
        limit=limit
    )

    return [
        ScoreModel.model_validate(score, from_attributes=True) \
                  .model_dump(exclude=['user'])
        for score in top_plays
    ]
