
from app.common.database.repositories import usercount as db_usercount
from app.common.cache import usercount as redis_usercount

from datetime import timedelta, datetime

import logging
import config
import time
import app

logger = logging.getLogger('usercount-job')

def sleep(seconds: float):
    while seconds > 0:
        time.sleep(1)
        seconds -= 1

        if app.session.jobs._shutdown:
            # Shutdown call
            logger.warning('Shutting down...')
            exit()

def update():
    """Add entries of current usercount inside database"""
    last_entry = db_usercount.fetch_last()

    if last_entry:
        time_since_last_entry = (datetime.now() - last_entry.time).total_seconds()

        if time_since_last_entry <= config.USERCOUNT_UPDATE_INTERVAL:
            next_entry_time = abs(time_since_last_entry - config.USERCOUNT_UPDATE_INTERVAL)
            logger.info(f'Next entry time: {round(next_entry_time, 2)} seconds')

            # Sleep until next entry time
            sleep(next_entry_time)

    while True:
        db_usercount.create(count := redis_usercount.get())
        logger.info(
            f'Created usercount entry ({count} players).'
        )

        if rows := db_usercount.delete_old(timedelta(weeks=1)):
            logger.info(
                f'Deleted old usercount entries ({rows} rows affected).'
            )

        sleep(config.USERCOUNT_UPDATE_INTERVAL)
