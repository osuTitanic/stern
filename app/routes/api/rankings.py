
from flask import Blueprint, abort, request
from flask_pydantic import validate
from typing import List

from app.common.database.repositories import histories, users, stats
from app.common.cache import leaderboards
from app.common.constants import GameMode
from app.common.database import DBUser
from app.models import UserModel

router = Blueprint("rankings", __name__)

@router.get('/<order_type>/<mode>')
@validate()
def rankings(
    order_type: str,
    mode: str
) -> List[dict]:
    if (mode := GameMode.from_alias(mode)) is None:
        return abort(400)

    if order_type not in ('performance', 'rscore', 'tscore'):
        return abort(400)

    limit = max(1, min(50, request.args.get('limit', default=50, type=int)))
    offset = request.args.get('offset', default=0, type=int)

    # Any two letter country code
    country = request.args.get('country', default=None, type=str)

    # Get current rankings according to redis
    users_top = leaderboards.top_players(
        mode.value,
        offset,
        limit,
        type=order_type,
        country=country.lower()
             if country else None
    )

    # Fetch user info from database
    users_db = users.fetch_many(
        tuple([user[0] for user in users_top]),
        DBUser.stats
    )

    # Sort users based on redis leaderboard
    sorted_users = [
        next(filter(lambda db: db.id == id, users_db))
        for id, score in users_top
    ]

    for index, user in enumerate(sorted_users):
        user.stats.sort(key=lambda x: x.mode)

        # Check if rank in redis has changed
        if (index + 1) != user.stats[mode].rank:
            user.stats[mode].rank = index + 1

            stats.update(
                user.id,
                mode,
                {'rank': user.stats[mode].rank}
            )

            histories.update_rank(user.stats[mode], user.country)
            users.fetch_many.cache_clear()

    return [
        {
            'user_id': user[0],
            'pp': user[1],
            'rank': index + offset + 1,
            'user': UserModel.model_validate(
                sorted_users[index],
                from_attributes=True
            ).model_dump()
        }
        for index, user in enumerate(users_top)
    ]
