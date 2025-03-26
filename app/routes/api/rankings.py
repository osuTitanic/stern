
from flask import Blueprint, request
from flask_pydantic import validate
from typing import List, Tuple

from app.common.database.repositories import users, stats
from app.common.constants import GameMode, COUNTRIES
from app.common.cache import leaderboards
from app.common.database import DBUser
from app.models import UserModel

import utils
import app

router = Blueprint("rankings", __name__)

def format_country_response(countries: List[dict]) -> List[dict]:
    return [
        {
            'rank': index + 1,
            'country_name': COUNTRIES[country['name'].upper()],
            'country_acronym': country['name'].upper(),
            'total_performance': country['total_performance'],
            'total_rscore': country['total_rscore'],
            'total_tscore': country['total_tscore'],
            'total_users': country['total_users'],
            'average_performance': country['average_pp']
        }
        for index, country in enumerate(countries)
    ]

def format_response(
    leaderboard: Tuple[int, int],
    users: List[DBUser],
    mode: GameMode,
    offset: int = 0
) -> List[dict]:
    return [
        {
            'index': index + offset + 1,
            'global_rank': leaderboards.global_rank(user[0], mode),
            'country_rank': leaderboards.country_rank(user[0], mode, users[index].country),
            'score_rank': leaderboards.score_rank(user[0], mode),
            'score_rank_country': leaderboards.score_rank_country(user[0], mode, users[index].country),
            'total_score_rank': leaderboards.total_score_rank(user[0], mode),
            'total_score_rank_country': leaderboards.total_score_rank_country(user[0], mode, users[index].country),
            'ppv1_rank': leaderboards.ppv1_rank(user[0], mode),
            'ppv1_rank_country': leaderboards.ppv1_country_rank(user[0], mode, users[index].country),
            'user_id': user[0],
            'score': user[1],
            'user': UserModel.model_validate(
                users[index],
                from_attributes=True
            ).model_dump()
        }
        for index, user in enumerate(leaderboard)
    ]

@router.get('/<order_type>/<mode>')
@validate()
def rankings(
    order_type: str,
    mode: str
) -> List[dict]:
    if (mode := GameMode.from_alias(mode)) is None:
        return {
            'error': 400,
            'details': 'The requested mode does not exist.'
        }, 400

    if order_type not in ('performance', 'rscore', 'tscore', 'country', 'ppv1'):
        return {
            'error': 400,
            'details': 'The requested type does not exist.'
        }, 400

    limit = max(1, min(50, request.args.get('limit', default=50, type=int)))
    offset = request.args.get('offset', default=0, type=int)

    # Any two letter country code
    country = request.args.get('country', default=None, type=str)

    if order_type == 'country':
        # Get country rankings
        return format_country_response(
            leaderboards.top_countries(mode)
        )

    with app.session.database.managed_session() as session:
        leaderboard = leaderboards.top_players(
            mode.value,
            offset,
            limit,
            order_type,
            country=(
                country.lower()
                if country else None
            )
        )

        # Fetch user info from database
        user_objects = users.fetch_many(
            tuple([user[0] for user in leaderboard]),
            DBUser.stats,
            session=session
        )

        # Sort users based on redis leaderboard
        sorted_users = [
            next(filter(lambda db: db.id == id, user_objects))
            for id, _ in leaderboard
        ]

        return format_response(
            leaderboard, sorted_users,
            mode, offset
        )
