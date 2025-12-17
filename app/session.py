
from .common.cache.events import EventQueue
from .common.database import Postgres
from .common.storage import Storage
from .common.config import Config

from concurrent.futures import ThreadPoolExecutor
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

logger = logging.getLogger('stern')
last_rank_sync = time.time()
startup_time = time.time()

requests = Session()
executor = ThreadPoolExecutor(max_workers=2)
requests.headers = {'User-Agent': f'osuTitanic/stern ({config.DOMAIN_NAME})'}

retries = Retry(
    total=4,
    backoff_factor=0.3,
    status_forcelist=[500, 502, 503, 504]
)
requests.mount('http://', HTTPAdapter(max_retries=retries))
requests.mount('https://', HTTPAdapter(max_retries=retries))
