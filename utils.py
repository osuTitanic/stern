
from flask import render_template as _render_template

from app.common.database import DBScore, DBStats
from app.common.database.repositories import stats
from app.common.cache import leaderboards

from datetime import datetime
from typing import List

import hashlib
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
        total_users=int(app.session.redis.get('bancho:totalusers'))
    )

    return _render_template(
        name,
        **kwargs
    )

def sync_ranks(user_stats: List[DBStats]) -> None:
    """Sync cached rank with database"""
    for mode in user_stats:
        redis_rank = leaderboards.global_rank(
            mode.user_id,
            mode.mode
        )

        if redis_rank != mode.rank:
            # Redis rank was updated
            stats.update(
                mode.user_id,
                mode.mode,
                {
                    'rank': redis_rank
                }
            )
