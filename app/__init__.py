
from . import session
from . import common
from . import routes

from flask import Flask

flask = Flask(
    __name__,
    static_url_path='',
    static_folder='static',
    template_folder='templates'
)

flask.register_blueprint(routes.router)
