
from __future__ import annotations
from typing import Tuple

from flask import request, current_app, abort, Response
from flask import render_template as _render_template
from datetime import datetime, timedelta
from jinja2 import TemplateNotFound
from sqlalchemy.orm import Session
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
import unicodedata
import config
import app
import io
import re

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
                read=False,
                session=context.get('session')
            )
        })

    return _render_template(
        template_name,
        **context
    )

def render_error(
    code: int,
    type: str | None = None,
    description: str | None = None
) -> Response:
    """Render error page with custom template if available"""
    template_name = (
        f'errors/default/{code}.html' if type is None else
        f'errors/custom/{type}.html'
    )

    if not template_exists(template_name):
        # Render default error page
        return abort(code)

    content = render_template(
        template_name,
        css='error.css',
        title=f'{description or code} - Titanic!',
        site_title=f'{description or code} - Titanic!',
        site_description='An error has occurred.',
        status_code=code
    )

    return Response(
        content,
        status=code,
        mimetype='text/html'
    )

def template_exists(template_name: str) -> bool:
    """Check if a template exists"""
    try:
        current_app.jinja_env.get_template(template_name)
        return True
    except TemplateNotFound:
        return False

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
    target_size: int | None = None,
) -> bytes:
    img = Image.open(io.BytesIO(image))
    img = img.resize((target_size, target_size))
    image_buffer = io.BytesIO()
    img.save(image_buffer, format='PNG')
    return image_buffer.getvalue()

def resize_and_crop_image(
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

def secure_filename(filename: str) -> str:
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")
    filename = re.compile(r"[^A-Za-z0-9_.-]").sub(" ", filename)
    filename = re.compile(r"\s+").sub(" ", filename)
    return filename.strip()

@caching.ttl_cache(ttl=900)
def fetch_average_topic_views() -> int:
    return int(topics.fetch_average_views())
