
from .common.logging import Console, File

from . import constants
from . import accounts
from . import session
from . import bbcode
from . import common
from . import routes
from . import uwsgi
from . import wiki
from . import git

from .filters import get_handle
from .app import flask
from . import handlers

import logging
import config

logging.basicConfig(
    format='[%(asctime)s] - <%(name)s> %(levelname)s: %(message)s',
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    handlers=[Console, File]
)
git.initialize_repository()
