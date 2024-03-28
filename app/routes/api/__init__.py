
from flask import Blueprint

from . import notifications
from . import multiplayer
from . import beatmaps
from . import rankings
from . import profile
from . import groups
from . import scores
from . import bbcode
from . import graph
from . import stats

router = Blueprint("api", __name__)
router.register_blueprint(notifications.router, url_prefix="/notifications")
router.register_blueprint(multiplayer.router, url_prefix="/multiplayer")
router.register_blueprint(beatmaps.router, url_prefix="/beatmaps")
router.register_blueprint(rankings.router, url_prefix="/rankings")
router.register_blueprint(profile.router, url_prefix="/profile")
router.register_blueprint(groups.router, url_prefix="/groups")
router.register_blueprint(scores.router, url_prefix="/scores")
router.register_blueprint(bbcode.router, url_prefix="/bbcode")
router.register_blueprint(graph.router, url_prefix="/graph")
router.register_blueprint(stats.router, url_prefix="/stats")
