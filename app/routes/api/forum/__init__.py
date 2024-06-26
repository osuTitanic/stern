
from flask import Blueprint

from . import subscriptions
from . import bookmarks

router = Blueprint("forum-api", __name__)
router.register_blueprint(subscriptions.router)
router.register_blueprint(bookmarks.router)
