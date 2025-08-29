
from werkzeug.exceptions import *
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_squeeze import Squeeze
from flask import Flask

from . import accounts
from . import routes

import config
import utils

flask = Flask(
    __name__,
    static_url_path='',
    static_folder='static',
    template_folder='templates'
)

csrf = CSRFProtect()
csrf.init_app(flask)

login_manager = LoginManager()
login_manager.init_app(flask)

flask.register_blueprint(routes.router)
flask.secret_key = config.FRONTEND_SECRET_KEY
flask.config['FLASK_PYDANTIC_VALIDATION_ERROR_RAISE'] = True

if not config.DEBUG:
    minify = Squeeze()
    minify.init_app(flask)
