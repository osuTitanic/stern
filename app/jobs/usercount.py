
from app.common.database.repositories import usercount as db_usercount
from app.common.cache import usercount as redis_usercount

import config
import time
import app

def sleep(seconds: int):
    for _ in range(seconds):
        time.sleep(1)

        if app.session.jobs._shutdown:
            # Shutdown call
            exit()

def update():
    """Add entries of current usercount inside database"""
    while True:
        count = db_usercount.create(redis_usercount.get()).count
        app.session.logger.debug(
            f'Created usercount entry ({count} players).'
        )

        if rows := db_usercount.delete_old():
            app.session.logger.debug(
                f'Deleted old usercount entries ({rows} rows affected).'
            )

        sleep(config.USERCOUNT_UPDATE_INTERVAL)
