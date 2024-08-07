
from flask import Blueprint, Response, request
from flask_pydantic import validate
from typing import List

from app.common.database.repositories import scores, users
from app.common.constants import GameMode
from app.models import ScoreModel

import app

router = Blueprint("top", __name__)

@router.get('/<user_id>/top/<mode>')
@validate()
def top_plays(
    user_id: str,
    mode: str
) -> List[dict]:
    with app.session.database.managed_session() as session:
        if not user_id.isdigit():
            # Lookup user by username
            if not (user := users.fetch_by_name_extended(user_id, session=session)):
                return {
                    'error': 404,
                    'details': 'The requested user could not be found.'
                }, 404

            user_id = user.id

        if (mode := GameMode.from_alias(mode)) is None:
            return {
                'error': 404,
                'details': 'The requested mode does not exist.'
            }, 404

        offset = request.args.get('offset', default=0, type=int)
        limit = max(1, min(50, request.args.get('limit', default=50, type=int)))

        top_plays = scores.fetch_top_scores(
            int(user_id),
            mode.value,
            offset=offset,
            limit=limit,
            session=session
        )

        top_count = scores.fetch_top_scores_count(
            int(user_id),
            mode.value,
            session=session
        )

        return {
            'count': top_count,
            'scores': [
                ScoreModel.model_validate(score, from_attributes=True) \
                          .model_dump(exclude=['user'])
                for score in top_plays
            ]
        }
