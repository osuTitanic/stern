
from flask import Blueprint

from . import multiplayer
from . import beatmapset
from . import changelog
from . import download
from . import rankings
from . import beatmap
from . import sitemap
from . import groups
from . import scores
from . import avatar
from . import users
from . import wiki
from . import home

router = Blueprint("public", __name__)
router.register_blueprint(download.router, url_prefix='/download')
router.register_blueprint(multiplayer.router, url_prefix='/mp')
router.register_blueprint(beatmapset.router, url_prefix='/')
router.register_blueprint(changelog.router, url_prefix='/')
router.register_blueprint(sitemap.router, url_prefix='/')
router.register_blueprint(rankings.router, url_prefix='/rankings')
router.register_blueprint(beatmap.router, url_prefix='/')
router.register_blueprint(wiki.router, url_prefix='/wiki')
router.register_blueprint(scores.router, url_prefix='/scores')
router.register_blueprint(avatar.router, url_prefix='/a')
router.register_blueprint(groups.router, url_prefix='/g')
router.register_blueprint(users.router, url_prefix='/u')
router.register_blueprint(home.router, url_prefix='/')
