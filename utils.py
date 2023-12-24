
from flask import render_template as _render_template
from flask import Request, request

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
import os

os.makedirs(f'{config.DATA_PATH}/avatars', exist_ok=True)

if not os.path.isfile(f'{config.DATA_PATH}/geolite.mmdb'):
    location.download_database()

def render_template(name: str, **kwargs) -> str:
    """This will automatically fetch all the required data for bancho-stats"""
    kwargs.update(
        total_scores=int(app.session.redis.get('bancho:totalscores') or 0),
        online_users=int(app.session.redis.get('bancho:users') or 0),
        total_users=int(app.session.redis.get('bancho:totalusers') or 0),
        show_login=request.args.get('login', False, type=bool),
        constants=constants,
        location=location,
        config=config,
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

def sync_ranks(user: DBUser) -> None:
    """Sync cached rank with database"""
    try:
        app.session.logger.debug(f'[{user.name}] Trying to update rank from cache...')

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
                    }
                )
                user_stats.rank = global_rank

                # Update rank history
                histories.update_rank(user_stats, user.country)

                app.session.logger.debug(
                    f'[{user.name}] Updated rank to {global_rank}'
                )
    except Exception as e:
        app.session.logging.error(
            f'[{user.name}] Failed to update user rank: {e}',
            exc_info=e
        )

def update_ppv1(user: DBUser):
    """Update ppv1 calculations for a player"""
    try:
        app.session.logger.debug(f'[{user.name}] Trying to update ppv1 calculations...')

        for user_stats in user.stats:
            if user_stats.playcount <= 0:
                continue

            best_scores = scores.fetch_best(user.id, user_stats.mode, not config.APPROVED_MAP_REWARDS)
            user_stats.ppv1 = performance.calculate_weighted_ppv1(best_scores)

            stats.update(
                user.id,
                user_stats.mode,
                {
                    'ppv1': user_stats.ppv1
                }
            )

            leaderboards.update(
                user_stats,
                user.country
            )

            histories.update_rank(
                user_stats,
                user.country
            )
    except Exception as e:
        app.session.logging.error(
            f'[{user.name}] Failed to update ppv1 calculations: {e}',
            exc_info=e
        )

def resolve_ip_address(request: Request):
    ip = request.headers.get("CF-Connecting-IP")

    if ip is None:
        forwards = request.headers.get("X-Forwarded-For")

    if forwards:
        ip = forwards.split(",")[0]
    else:
        ip = request.headers.get("X-Real-IP")

    if ip is None:
        ip = request.environ['REMOTE_ADDR']

    return ip.strip()
