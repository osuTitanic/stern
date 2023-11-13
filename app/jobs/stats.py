
from app.common.database import DBUser
from app.common.cache import usercount as redis_usercount
from app.common.database.repositories import usercount as db_usercount
from app.common.database.repositories import (
    beatmaps,
    scores,
    users
)

from datetime import timedelta, datetime

import logging
import config
import utils
import app

logger = logging.getLogger('stats-job')

def update_stats():
    """Update the total users, beatmaps and scores to redis"""
    app.session.redis.set('bancho:totalusers', users.fetch_count())
    app.session.redis.set('bancho:totalbeatmaps', beatmaps.fetch_count())
    app.session.redis.set('bancho:totalscores', scores.fetch_total_count())
    app.session.jobs.sleep(config.USERCOUNT_UPDATE_INTERVAL)

def update_usercount():
    """Add entries of current usercount inside database"""
    last_entry = db_usercount.fetch_last()

    if last_entry:
        last_entry_time = last_entry.time.replace(tzinfo=None)
        time_since_last_entry = (datetime.now() - last_entry_time).total_seconds()

        if time_since_last_entry <= config.USERCOUNT_UPDATE_INTERVAL:
            next_entry_time = abs(time_since_last_entry - config.USERCOUNT_UPDATE_INTERVAL)
            logger.debug(f'Next entry time: {round(next_entry_time, 2)} seconds')

            # Sleep until next entry time
            app.session.jobs.sleep(next_entry_time)

    while True:
        db_usercount.create(count := redis_usercount.get())
        logger.debug(
            f'Created usercount entry ({count} players).'
        )

        if rows := db_usercount.delete_old(timedelta(weeks=1)):
            logger.debug(
                f'Deleted old usercount entries ({rows} rows affected).'
            )

        app.session.jobs.sleep(config.USERCOUNT_UPDATE_INTERVAL)

def update_ranks():
    """Update the rank history for every user after one hour."""
    while True:
        active_users = users.fetch_active(
            timedelta(days=90),
            DBUser.stats
        )

        for user in active_users:
            utils.sync_ranks(user)

        app.session.jobs.sleep(3600)
