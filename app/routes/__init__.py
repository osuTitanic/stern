

from flask import Blueprint

from . import beatmapset
from . import redirects
from . import download
from . import beatmap
from . import search
from . import users
from . import home
from . import api

router = Blueprint("routes", __name__)
router.register_blueprint(download.router, url_prefix='/download')
router.register_blueprint(beatmapset.router, url_prefix='/s')
router.register_blueprint(redirects.router, url_prefix='/')
router.register_blueprint(beatmap.router, url_prefix='/b')
router.register_blueprint(search.router, url_prefix='/beatmapsets')
router.register_blueprint(users.router, url_prefix='/u')
router.register_blueprint(home.router, url_prefix='/')
router.register_blueprint(api.router, url_prefix='/api')
