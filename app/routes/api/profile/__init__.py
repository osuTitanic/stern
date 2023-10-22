
from flask import Blueprint

from . import first
from . import top

router = Blueprint("profile", __name__)
router.register_blueprint(first.router)
router.register_blueprint(top.router)
