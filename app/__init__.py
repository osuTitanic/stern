
from .common.logging import Console, File

from . import constants
from . import session
from . import bbcode
from . import common
from . import routes

from .app import flask, get_handle

import logging
import config

logging.basicConfig(
    format='[%(asctime)s] - <%(name)s> %(levelname)s: %(message)s',
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    handlers=[Console, File]
)
