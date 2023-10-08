
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
    db_usercount.create(redis_usercount.get())
    sleep(config.USERCOUNT_UPDATE_INTERVAL)
