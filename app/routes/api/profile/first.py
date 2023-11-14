
from flask import Blueprint, Response, request
from flask_pydantic import validate
from typing import List

from app.common.database.repositories import scores, users
from app.common.constants import GameMode
from app.models import ScoreModel

router = Blueprint("first", __name__)

@router.get('/<user_id>/first/<mode>')
@validate()
def leader_scores(
    user_id: str,
    mode: str
) -> List[dict]:
    if not user_id.isdigit():
        # Lookup user by username
        if not (user := users.fetch_by_name_extended(user_id)):
            return Response(
                response=(),
                status=404,
                mimetype='application/json'
            )

        user_id = user.id

    if (mode := GameMode.from_alias(mode)) is None:
        return Response(
            response={},
            status=404,
            mimetype='application/json'
        )

    offset = request.args.get('offset', default=0, type=int)
    limit = max(1, min(50, request.args.get('limit', default=50, type=int)))

    top_plays = scores.fetch_leader_scores(
        int(user_id),
        mode,
        offset=offset,
        limit=limit
    )

    return [
        ScoreModel.model_validate(score, from_attributes=True) \
                  .model_dump(exclude=['user'])
        for score in top_plays
    ]
