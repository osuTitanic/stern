
from flask import render_template as _render_template

from app.common.database.repositories import stats, histories
from app.common.database import DBScore, DBUser
from app.common.cache import leaderboards
from datetime import datetime
from typing import List

import hashlib
import config
import app

def compute_score_checksum(score: DBScore) -> str:
    return hashlib.md5(
        '{}p{}o{}o{}t{}a{}r{}e{}y{}o{}u{}{}{}'.format(
            (score.n100 + score.n300),
            score.n50,
            score.nGeki,
            score.nKatu,
            score.nMiss,
            score.beatmap.md5,
            score.max_combo,
            score.perfect,
            score.user.name,
            score.total_score,
            score.grade,
            score.mods,
            (not score.failtime) # (passed)
        ).encode()
    ).hexdigest()

def get_ticks(dt) -> int:
    dt = dt.replace(tzinfo=None)
    return int((dt - datetime(1, 1, 1)).total_seconds() * 10000000)

def render_template(name: str, **kwargs) -> str:
    """This will automatically fetch all the required data for bancho-stats"""
    kwargs.update(
        total_scores=int(app.session.redis.get('bancho:totalscores')),
        online_users=int(app.session.redis.get('bancho:users')),
        total_users=int(app.session.redis.get('bancho:totalusers')),
        config=config
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
