
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

try:
    import uwsgidecorators

    uwsgidecorators.postfork(uwsgidecorators.thread(jobs.stats.update_ranks))
    uwsgidecorators.postfork(uwsgidecorators.thread(jobs.stats.update_stats))
    uwsgidecorators.postfork(uwsgidecorators.thread(jobs.stats.update_usercount))
except ImportError:
    session.jobs.submit(jobs.stats.update_usercount)
    session.jobs.submit(jobs.stats.update_stats)
    session.jobs.submit(jobs.stats.update_ranks)
