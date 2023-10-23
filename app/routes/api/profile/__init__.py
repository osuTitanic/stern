
from flask import Blueprint

from . import activity
from . import profile
from . import history
from . import plays
from . import first
from . import top

router = Blueprint("profile", __name__)
router.register_blueprint(activity.router)
router.register_blueprint(profile.router)
router.register_blueprint(history.router)
router.register_blueprint(first.router)
router.register_blueprint(plays.router)
router.register_blueprint(top.router)
