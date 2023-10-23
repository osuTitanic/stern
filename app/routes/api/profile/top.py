
from flask import Blueprint, abort, request
from flask_pydantic import validate
from typing import List

from app.common.database.repositories import scores
from app.common.constants import GameMode
from app.models import ScoreModel

router = Blueprint("top", __name__)

import config

@router.get('/<user_id>/top/<mode>')
@validate()
def top_plays(
    user_id: int,
    mode: str
) -> List[dict]:
    if (mode := GameMode.from_alias(mode)) is None:
        return abort(400)

    offset = request.args.get('offset', default=0, type=int)
    limit = max(1, min(50, request.args.get('limit', default=50, type=int)))

    top_plays = scores.fetch_top_scores(
        user_id,
        mode.value,
        offset=offset,
        limit=limit
    )

    return [
        ScoreModel.model_validate(score, from_attributes=True) \
                  .model_dump(exclude=['user'])
        for score in top_plays
    ]
