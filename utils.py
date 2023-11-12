
from flask import render_template as _render_template

from app.common.database.repositories import stats, histories
from app.common.cache import leaderboards
from app.common.database import DBUser
from app.common import constants

import config
import app

def render_template(name: str, **kwargs) -> str:
    """This will automatically fetch all the required data for bancho-stats"""
    kwargs.update(
        total_scores=int(app.session.redis.get('bancho:totalscores')) or 0,
        online_users=int(app.session.redis.get('bancho:users')) or 0,
        total_users=int(app.session.redis.get('bancho:totalusers')) or 0,
        constants=constants,
        config=config,
    )

    return _render_template(
        name,
        **kwargs
    )

def sync_ranks(user: DBUser) -> None:
    """Sync cached rank with database"""
    try:
        app.session.logger.debug(f'[{user.name}] Trying to update user rank from cache...')

        for user_stats in user.stats:
            if user_stats.playcount <= 0:
                continue

            global_rank = leaderboards.global_rank(user.id, user_stats.mode)

            if user_stats.rank != global_rank:
                # Database rank desynced from redis
                stats.update(
                    user.id,
                    user_stats.mode,
                    {
                        'rank': global_rank
                    }
                )

                # Update rank history
                histories.update_rank(user_stats, user.country)

                app.session.logger.debug(
                    f'[{user.name}] Updated rank from {user_stats.rank} to {global_rank}'
                )

    except Exception as e:
        app.session.logging.error(
            f'[{user.name}] Failed to update user rank: {e}',
            exc_info=e
        )
