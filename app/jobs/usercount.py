
from app.common.database.repositories import usercount as db_usercount
from app.common.cache import usercount as redis_usercount

from datetime import timedelta, datetime

import logging
import config
import time
import app

logger = logging.getLogger('usercount-job')

def sleep(seconds: int):
    for _ in range(seconds):
        time.sleep(1)

        if app.session.jobs._shutdown:
            # Shutdown call
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
        count = db_usercount.create(redis_usercount.get()).count
        logger.debug(
            f'Created usercount entry ({count} players).'
        )

        if rows := db_usercount.delete_old(timedelta(weeks=1)):
            logger.debug(
                f'Deleted old usercount entries ({rows} rows affected).'
            )

        sleep(config.USERCOUNT_UPDATE_INTERVAL)
