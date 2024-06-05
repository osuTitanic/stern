
from __future__ import annotations

from sqlalchemy.orm import Session
from flask import render_template as _render_template
from flask import request
from PIL import Image

from app.common.database import DBUser, repositories, topics
from app.common.database.repositories import wrapper
from app.common.cache import leaderboards, status
from app.common.helpers.external import location
from app.common.helpers import caching, analytics, ip
from app.common.database import DBUser
from app.common import constants

from app.common.database import (
    notifications,
    histories,
    scores,
    stats
)

import flask_login
import config
import app
import io

def render_template(template_name: str, **context) -> str:
    """This will automatically append the required data to the context for rendering pages"""
    context.update(
        total_scores=int(app.session.redis.get('bancho:totalscores') or 0),
        online_users=int(app.session.redis.get('bancho:users') or 0),
        total_users=int(app.session.redis.get('bancho:totalusers') or 0),
        show_login=request.args.get('login', False, type=bool),
        repositories=repositories,
        constants=constants,
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
def sync_ranks(user: DBUser, session: Session | None = None) -> None:
    """Sync cached rank with database"""
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

def track(
    event: str,
    properties: dict | None,
    user: DBUser | None
) -> None:
    if not user:
        return

    ip_address = ip.resolve_ip_address_flask(request)
    device_id = status.device_id(user.id)

    analytics.track(
        event,
        user_id=user.id,
        device_id=device_id,
        ip=ip_address,
        event_properties=properties,
        user_properties={
            'user_id': user.id,
            'name': user.name,
            'country': user.country
        }
    )
