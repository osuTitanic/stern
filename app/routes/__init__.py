

from flask import Blueprint

from . import redirects
from . import download
from . import beatmap
from . import users
from . import graph
from . import home

router = Blueprint("routes", __name__)
router.register_blueprint(download.router, url_prefix='/download')
router.register_blueprint(graph.router, url_prefix='/graph')
router.register_blueprint(redirects.router, url_prefix='/')
router.register_blueprint(beatmap.router, url_prefix='/b')
router.register_blueprint(users.router, url_prefix='/u')
router.register_blueprint(home.router, url_prefix='/')
