
from flask import Blueprint

from . import achievements
from . import favourites
from . import playstyle
from . import activity
from . import beatmaps
from . import profile
from . import history
from . import friends
from . import status
from . import pinned
from . import recent
from . import plays
from . import first
from . import top

router = Blueprint("profile", __name__)
router.register_blueprint(achievements.router)
router.register_blueprint(favourites.router)
router.register_blueprint(playstyle.router)
router.register_blueprint(activity.router)
router.register_blueprint(beatmaps.router)
router.register_blueprint(profile.router)
router.register_blueprint(history.router)
router.register_blueprint(friends.router)
router.register_blueprint(status.router)
router.register_blueprint(pinned.router)
router.register_blueprint(recent.router)
router.register_blueprint(first.router)
router.register_blueprint(plays.router)
router.register_blueprint(top.router)
