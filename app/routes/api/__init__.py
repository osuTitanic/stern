
from flask import Blueprint

from . import beatmapsets
from . import rankings
from . import profile
from . import groups
from . import graph

router = Blueprint("api", __name__)
router.register_blueprint(beatmapsets.router, url_prefix="/beatmapsets")
router.register_blueprint(rankings.router, url_prefix="/rankings")
router.register_blueprint(profile.router, url_prefix="/profile")
router.register_blueprint(groups.router, url_prefix="/groups")
router.register_blueprint(graph.router, url_prefix="/graph")
