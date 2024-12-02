
from flask import Blueprint, Response
from flask_pydantic import validate

from app.common.database.repositories import users
from app.common.cache import leaderboards
from app.common.constants import level
from app.models import UserModel

import app

router = Blueprint("profile", __name__)

def calculate_level(total_score: int) -> int:
    next_level = level.NEXT_LEVEL
    total_score = min(total_score, next_level[-1])

    index = 0
    score = 0

    while score + next_level[index] < total_score:
        score += next_level[index]
        index += 1

    return round((index + 1) + (total_score - score) / next_level[index])

@router.get('/<user_id>')
@validate()
def profile(user_id: str) -> dict:
    with app.session.database.managed_session() as session:
        if not user_id.isdigit():
            # Lookup user by username
            if not (user := users.fetch_by_name_extended(user_id, session=session)):
                return {
                    'error': 404,
                    'details': 'The requested user could not be found.'
                }, 404

        else:
            if not (user := users.fetch_by_id(user_id, session=session)):
                return {
                    'error': 404,
                    'details': 'The requested user could not be found.'
                }, 404

        user.stats.sort(key=lambda x: x.mode)

        model = UserModel.model_validate(user, from_attributes=True)
        response = model.model_dump()

        for stats in response['stats']:
            stats['level'] = calculate_level(stats['tscore'])
            stats['rankings'] = {
                'global': leaderboards.global_rank(user.id, stats['mode']),
                'country': leaderboards.country_rank(user.id, stats['mode'], user.country),
                'ppv1': leaderboards.ppv1_rank(user.id, stats['mode']),
                'score': leaderboards.score_rank(user.id, stats['mode']),
                'total_score': leaderboards.total_score_rank(user.id, stats['mode']),
                'clears': leaderboards.clears_rank(user.id, stats['mode']),
            }

        return response
