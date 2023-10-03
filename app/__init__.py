
from . import session
from . import common
from . import routes

from flask import Flask

flask = Flask(
    __name__,
    static_url_path='',
    static_folder='app/static'
)

flask.register_blueprint(routes.router)
