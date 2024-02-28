
from flask import Blueprint

from . import beatmap
from . import search

router = Blueprint('beatmaps', __name__)
router.register_blueprint(beatmap.router)
router.register_blueprint(search.router)
