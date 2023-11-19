
from flask import Blueprint

from . import overview
from . import profile

router = Blueprint('settings', __name__)
router.register_blueprint(overview.router)
router.register_blueprint(profile.router)
