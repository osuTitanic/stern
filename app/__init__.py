
from .common.logging import Console, File

from . import constants
from . import session
from . import common
from . import routes
from . import jobs

from .app import flask

import logging
import config

logging.basicConfig(
    format='[%(asctime)s] - <%(name)s> %(levelname)s: %(message)s',
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    handlers=[Console, File]
)

session.jobs.submit(jobs.stats.update_usercount)
session.jobs.submit(jobs.stats.update_stats)
session.jobs.submit(jobs.stats.update_ranks)
