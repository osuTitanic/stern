
from flask import Blueprint

from . import top

router = Blueprint("profile", __name__)
router.register_blueprint(top.router)
