
from flask import Blueprint, Response, request
from flask_pydantic import validate
from typing import List

from app.common.database.repositories import scores, users
from app.common.constants import GameMode
from app.models import ScoreModel

import app

router = Blueprint("first", __name__)

@router.get('/<user_id>/first/<mode>')
@validate()
def leader_scores(
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
                'error': 400,
                'details': 'The requested mode does not exist.'
            }, 400

        offset = request.args.get('offset', default=0, type=int)
        limit = max(1, min(50, request.args.get('limit', default=50, type=int)))

        first_scores = scores.fetch_leader_scores(
            int(user_id),
            mode,
            offset=offset,
            limit=limit,
            session=session
        )

        first_count = scores.fetch_leader_count(
            int(user_id),
            mode,
            session=session
        )

        return {
            'count': first_count,
            'scores': [
                ScoreModel.model_validate(score, from_attributes=True) \
                          .model_dump(exclude=['user'])
                for score in first_scores
            ]
        }
