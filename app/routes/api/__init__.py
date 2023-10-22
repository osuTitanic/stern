
from flask import Blueprint

from . import profile

router = Blueprint("api", __name__)
router.register_blueprint(profile.router, url_prefix="/profile")
