
from flask import Blueprint

from . import search

router = Blueprint('beatmaps', __name__)
router.register_blueprint(search.router)
