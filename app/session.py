
from .common.cache.events import EventQueue
from .common.database import Postgres
from .common.storage import Storage

from requests import Session
from redis import Redis

import logging
import config
import time

database = Postgres(
    config.POSTGRES_USER,
    config.POSTGRES_PASSWORD,
    config.POSTGRES_HOST,
    config.POSTGRES_PORT
)

redis = Redis(
    config.REDIS_HOST,
    config.REDIS_PORT
)

events = EventQueue(
    name='bancho:events',
    connection=redis
)

logger = logging.getLogger('stern')
startup_time = time.time()

storage = Storage()
requests = Session()
requests.headers = {
    'User-Agent': 'osuTitanic/stern'
}
