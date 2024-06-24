
from flask import Blueprint

from . import favourites
from . import resources
from . import beatmap
from . import search

router = Blueprint('beatmaps', __name__)
router.register_blueprint(favourites.router)
router.register_blueprint(resources.router)
router.register_blueprint(beatmap.router)
router.register_blueprint(search.router)
