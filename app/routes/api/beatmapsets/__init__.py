
from flask import Blueprint

from . import search

router = Blueprint('beatmapsets', __name__)
router.register_blueprint(search.router)
