
from flask import Blueprint

from . import overview
from . import security
from . import profile
from . import friends

router = Blueprint('settings', __name__)
router.register_blueprint(overview.router)
router.register_blueprint(security.router)
router.register_blueprint(profile.router)
router.register_blueprint(friends.router)
