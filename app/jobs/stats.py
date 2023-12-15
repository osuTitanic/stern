
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
    while True:
        try:
            app.session.redis.set('bancho:totalusers', users.fetch_count())
            app.session.redis.set('bancho:totalbeatmaps', beatmaps.fetch_count())
            app.session.redis.set('bancho:totalscores', scores.fetch_total_count())
            app.session.jobs.sleep(config.USERCOUNT_UPDATE_INTERVAL)
        except Exception as e:
            app.session.logger.error(
                f"Failed to update stats: {e}",
                exc_info=e
            )

def update_usercount():
    """Add entries of current usercount inside database"""
    last_entry = db_usercount.fetch_last()

    if last_entry:
        last_entry_time = last_entry.time.replace(tzinfo=None)
        time_since_last_entry = (datetime.now() - last_entry_time).total_seconds()

        if time_since_last_entry <= config.USERCOUNT_UPDATE_INTERVAL:
            next_entry_time = abs(time_since_last_entry - config.USERCOUNT_UPDATE_INTERVAL)
            logger.debug(f'[usercount] -> Next entry time: {round(next_entry_time, 2)} seconds')

            # Sleep until next entry time
            app.session.jobs.sleep(next_entry_time)

    while True:
        try:
            db_usercount.create(count := redis_usercount.get())
            logger.debug(
                f'[usercount] -> Created usercount entry ({count} players).'
            )

            if rows := db_usercount.delete_old(timedelta(weeks=1)):
                logger.debug(
                    f'[usercount] -> Deleted old usercount entries ({rows} rows affected).'
                )

            app.session.jobs.sleep(config.USERCOUNT_UPDATE_INTERVAL)
        except Exception as e:
            app.session.logger.error(
                f"Failed to update usercount: {e}",
                exc_info=e
            )

def update_ranks():
    """Update the rank history for every user, every 15 minutes."""
    while True:
        try:
            app.session.jobs.logger.info('[ranks] -> Updating rank history...')

            active_users = users.fetch_active(
                timedelta(days=90),
                DBUser.stats
            )

            for user in active_users:
                utils.sync_ranks(user)
                app.session.jobs.logger.info(f'[ranks] -> Updated {user.name}')

                if app.session.jobs._shutdown:
                    exit()

            app.session.jobs.logger.info('[ranks] -> Done.')
            app.session.jobs.sleep(900)
        except Exception as e:
            app.session.logger.error(
                f"Failed to update ranks: {e}",
                exc_info=e
            )

def update_ppv1():
    """Update the ppv1 calculations for each user, every 2.5 hours."""
    while True:
        try:
            app.session.jobs.logger.info('[ppv1] -> Updating ppv1 calculations...')

            for user in users.fetch_all():
                utils.update_ppv1(user)
                app.session.jobs.logger.info(f'[ppv1] -> Updated {user.name}')

                if app.session.jobs._shutdown:
                    exit()

            app.session.jobs.logger.info('[ppv1] -> Done.')
            app.session.jobs.sleep(3600 * 2.5)
        except Exception as e:
            app.session.logger.error(
                f"Failed to update ppv1: {e}",
                exc_info=e
            )
