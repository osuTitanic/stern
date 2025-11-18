
from .common.logging import Console, File

from . import constants
from . import accounts
from . import session
from . import common
from . import routes
from . import uwsgi
from . import wiki

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

# Useless debug logging, very annoying
font_manager = logging.getLogger('matplotlib.font_manager')
font_manager.setLevel(logging.WARNING)
pillow_debug = logging.getLogger('PIL.PngImagePlugin')
pillow_debug.setLevel(logging.WARNING)
