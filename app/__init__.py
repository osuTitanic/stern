
from .logging import Console, File

from . import session
from . import common
from . import routes
from . import jobs

from flask import Flask

import logging

logging.basicConfig(
    format='[%(asctime)s] - <%(name)s> %(levelname)s: %(message)s',
    level=logging.INFO,
    handlers=[Console, File]
)

flask = Flask(
    __name__,
    static_url_path='',
    static_folder='static',
    template_folder='templates'
)

flask.register_blueprint(routes.router)
