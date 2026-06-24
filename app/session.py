
from .common.helpers.beatmaps import BeatmapResources
from .common.cache.events import EventQueue
from .common.database import Postgres
from .common.storage import Storage
from .common.config import Config

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests import Session
from redis import Redis

import logging
import time

config = Config()
database = Postgres(config)
storage = Storage(config)

redis = Redis(
    config.REDIS_HOST,
    config.REDIS_PORT
)
events = EventQueue(
    name='bancho:events',
    connection=redis
)
beatmaps = BeatmapResources(storage, redis)

logger = logging.getLogger('stern')
startup_time = time.time()

requests = Session()
requests.headers = {'User-Agent': f'osuTitanic/stern ({config.DOMAIN_NAME})'}

retries = Retry(
    total=4,
    backoff_factor=0.3,
    status_forcelist=[500, 502, 503, 504]
)
requests.mount('http://', HTTPAdapter(max_retries=retries))
requests.mount('https://', HTTPAdapter(max_retries=retries))
