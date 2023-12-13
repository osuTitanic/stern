
from .common.logging import Console, File

from . import constants
from . import session
from . import bbcode
from . import common
from . import routes
from . import jobs

from .app import flask, get_handle

import logging
import config

logging.basicConfig(
    format='[%(asctime)s] - <%(name)s> %(levelname)s: %(message)s',
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    handlers=[Console, File]
)

if not config.DEBUG:
    session.jobs.submit(jobs.stats.update_usercount)
    session.jobs.submit(jobs.stats.update_stats)
    session.jobs.submit(jobs.stats.update_ranks)
    session.jobs.submit(jobs.stats.update_ppv1)
