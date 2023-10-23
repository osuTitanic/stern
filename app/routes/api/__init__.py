
from flask import Blueprint

from . import rankings
from . import profile

router = Blueprint("api", __name__)
router.register_blueprint(rankings.router, url_prefix="/rankings")
router.register_blueprint(profile.router, url_prefix="/profile")
