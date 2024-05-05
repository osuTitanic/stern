
from __future__ import annotations

from sqlalchemy.orm import Session
from flask import render_template as _render_template
from flask import request
from PIL import Image

from app.common.database.repositories.wrapper import session_wrapper
from app.common.helpers.external import location
from app.common.helpers import performance
from app.common.cache import leaderboards
from app.common.database import DBUser
from app.common import constants

from app.common.database.repositories import (
    notifications,
    histories,
    scores,
    stats
)

import flask_login
import config
import app
import io

def render_template(name: str, **kwargs) -> str:
    """This will automatically append the required data to the context for rendering pages"""
    kwargs.update(
        total_scores=int(app.session.redis.get('bancho:totalscores') or 0),
        online_users=int(app.session.redis.get('bancho:users') or 0),
        total_users=int(app.session.redis.get('bancho:totalusers') or 0),
        show_login=request.args.get('login', False, type=bool),
        constants=constants,
        location=location,
        config=config
    )

    if not flask_login.current_user.is_anonymous:
        kwargs.update({
            'notification_count': notifications.fetch_count(
                flask_login.current_user.id,
                read=False
            )
        })

    return _render_template(
        name,
        **kwargs
    )

@session_wrapper
def sync_ranks(user: DBUser, session: Session | None = None) -> None:
    """Sync cached rank with database"""
    try:
        for user_stats in user.stats:
            if user_stats.playcount <= 0:
                continue

            global_rank = leaderboards.global_rank(
                user.id,
                user_stats.mode
            )

            if user_stats.rank != global_rank:
                # Database rank desynced from redis
                stats.update(
                    user.id,
                    user_stats.mode,
                    {
                        'rank': global_rank
                    },
                    session=session
                )
                user_stats.rank = global_rank

                # Update rank history
                histories.update_rank(user_stats, user.country, session=session)
    except Exception as e:
        app.session.logger.error(
            f'[{user.name}] Failed to update user rank: {e}',
            exc_info=e
        )

def resize_image(
    image: bytes,
    target_width: int | None = None,
    target_height: int | None = None
) -> bytes:
    image_buffer = io.BytesIO()

    img = Image.open(io.BytesIO(image))
    img = img.resize((target_width, target_height))
    img.save(image_buffer, format='PNG')

    return image_buffer.getvalue()
