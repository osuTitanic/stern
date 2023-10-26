
from flask import Blueprint, abort, request
from datetime import datetime, timedelta
from flask_pydantic import validate
from typing import List

from app.common.database.repositories import scores
from app.common.constants import GameMode
from app.models import ScoreModel

router = Blueprint("recent", __name__)

@router.get('/<user_id>/recent/<mode>')
@validate()
def recent_scores(
    user_id: int,
    mode: str
) -> List[dict]:
    if (mode := GameMode.from_alias(mode)) is None:
        return abort(400)

    try:
        if date_string := request.args.get('until'):
            until = datetime.fromisoformat(date_string)
        else:
            until = datetime.now() - timedelta(hours=24)
    except ValueError:
        return abort(400)

    # Limit time
    until = sorted((
        datetime.now() - timedelta(days=30),
        until,
        datetime.now()
    ))[1]

    recent_plays = scores.fetch_recent_until(
        user_id,
        mode,
        until
    )

    return [
        ScoreModel.model_validate(score, from_attributes=True) \
                  .model_dump(exclude=['user'])
        for score in recent_plays
    ]
