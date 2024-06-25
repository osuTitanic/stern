
from flask import Blueprint

from . import nomination
from . import favourites
from . import resources
from . import beatmap
from . import update
from . import search
from . import status

router = Blueprint('beatmaps', __name__)
router.register_blueprint(nomination.router)
router.register_blueprint(favourites.router)
router.register_blueprint(resources.router)
router.register_blueprint(beatmap.router)
router.register_blueprint(update.router)
router.register_blueprint(search.router)
router.register_blueprint(status.router)
