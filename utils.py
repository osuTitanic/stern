
from __future__ import annotations
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from flask import render_template as _render_template
from flask import request
from PIL import Image

from app.common.database.repositories import wrapper
from app.common.database import DBUser, DBBeatmapset
from app.common.helpers.external import location
from app.common.helpers import caching, browsers
from app.common.cache import leaderboards
from app.common import constants

from app.common.database import (
    notifications,
    repositories,
    histories,
    topics,
    stats
)

import flask_login
import config
import app
import io

def render_template(template_name: str, **context) -> str:
    """This will automatically append the required data to the context for rendering pages"""
    total_scores = 0
    online_users = 0
    total_users = 0

    try:
        total_scores = int(app.session.redis.get('bancho:totalscores') or 0)
        online_users = int(app.session.redis.get('bancho:users') or 0)
        total_users = int(app.session.redis.get('bancho:totalusers') or 0)
    except Exception as e:
        # Most likely failed to connect to redis instance
        app.session.logger.error(
            f'Failed to fetch bancho stats: {e}',
            exc_info=e
        )

    context.update(
        is_modern_browser=browsers.is_modern_browser(request.user_agent.string),
        is_ie=browsers.is_internet_explorer(request.user_agent.string),
        is_compact=request.args.get('compact', 0, type=int) == 1,
        total_scores=total_scores,
        online_users=online_users,
        total_users=total_users,
        repositories=repositories,
        timedelta=timedelta,
        constants=constants,
        datetime=datetime,
        location=location,
        config=config
    )

    if not flask_login.current_user.is_anonymous:
        context.update({
            'notification_count': notifications.fetch_count(
                flask_login.current_user.id,
                read=False
            )
        })

    return _render_template(
        template_name,
        **context
    )

@caching.ttl_cache(ttl=900)
def fetch_average_topic_views() -> int:
    return int(topics.fetch_average_views())

def on_sync_ranks_fail(e: Exception) -> None:
    app.session.logger.error(
        f'Failed to update user rank: {e}',
        exc_info=e
    )

@wrapper.exception_wrapper(on_sync_ranks_fail)
@wrapper.session_wrapper
def sync_ranks(user: DBUser, mode: int, session: Session = ...) -> None:
    """Sync cached rank with database"""
    user.stats.sort(key=lambda s:s.mode)
    user_stats = user.stats[mode]

    if user_stats.playcount <= 0:
        return

    global_rank = leaderboards.global_rank(
        user.id,
        user_stats.mode
    )

    if user_stats.rank != global_rank:
        # Database rank desynced from redis
        stats.update(
            user.id,
            user_stats.mode,
            {'rank': global_rank},
            session=session
        )
        user_stats.rank = global_rank

        # Update rank history
        histories.update_rank(
            user_stats,
            user.country,
            session=session
        )

def required_nominations(beatmapset: DBBeatmapset) -> bool:
    beatmap_modes = len(
        set(
            beatmap.mode
            for beatmap in beatmapset.beatmaps
        )
    )

    # NOTE: Beatmap requires 2 approvals + 1 for each other mode
    additional_modes = beatmap_modes - 1
    required_nominations = 2 + additional_modes

    return required_nominations

def resize_image(
    image: bytes,
    target_width: int | None = None,
    target_height: int | None = None
) -> bytes:
    image_buffer = io.BytesIO()

    img = Image.open(io.BytesIO(image))
    img = img.resize((target_width, target_height))
    img.save(image_buffer, format='JPEG')

    return image_buffer.getvalue()

def empty_image(
    width: int,
    height: int
) -> bytes:
    image_buffer = io.BytesIO()
    img = Image.new('RGB', (width, height), (0, 0, 0))
    img.save(image_buffer, format='JPEG')
    return image_buffer.getvalue()

@caching.ttl_cache(ttl=900)
def fetch_average_topic_views() -> int:
    return int(topics.fetch_average_views())
