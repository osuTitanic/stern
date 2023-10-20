
from .common.logging import Console, File

from . import constants
from . import session
from . import common
from . import routes
from . import jobs

from werkzeug.exceptions import NotFound
from datetime import datetime
from typing import Tuple
from flask import Flask

import timeago
import logging
import config
import utils
import re

logging.basicConfig(
    format='[%(asctime)s] - <%(name)s> %(levelname)s: %(message)s',
    level=logging.DEBUG if config.DEBUG else logging.INFO,
    handlers=[Console, File]
)

flask = Flask(
    __name__,
    static_url_path='',
    static_folder='static',
    template_folder='templates'
)

flask.register_blueprint(routes.router)

@flask.template_filter('timeago')
def timeago_formatting(date: datetime):
    return timeago.format(date.replace(tzinfo=None), datetime.now())

@flask.template_filter('round')
def get_rounded(num: float):
    return round(num, 2)

@flask.template_filter('playstyle')
def get_rounded(num: int):
    return common.constants.Playstyle(num)

@flask.template_filter('domain')
def get_domain(url: str) -> str:
    return re.search(r'https?://([A-Za-z_0-9.-]+).*', url) \
             .group(1)

@flask.template_filter('twitter_handle')
def get_handle(url: str) -> str:
    return re.search(r'https?://(www.)?(twitter|x)\.com/(@\w+|\w+)', url) \
             .group(3)

@flask.template_filter('short_mods')
def get_short(mods):
    return (
        common.constants.Mods(mods).short
        if mods else 'None'
    )

@flask.errorhandler(404)
def not_found(error: NotFound) -> Tuple[str, int]:
    return utils.render_template(
        content=error.description,
        name='404.html',
        css='404.css'
    ), 404
