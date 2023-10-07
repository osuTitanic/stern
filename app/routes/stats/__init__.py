
from flask import Blueprint

from . import activity

router = Blueprint("stats", __name__)
router.register_blueprint(activity.router)
