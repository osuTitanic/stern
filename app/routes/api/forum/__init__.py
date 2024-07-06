
from flask import Blueprint

from . import subscriptions
from . import bookmarks
from . import topics
from . import forum
from . import posts

router = Blueprint("forum-api", __name__)
router.register_blueprint(subscriptions.router)
router.register_blueprint(bookmarks.router)
router.register_blueprint(topics.router)
router.register_blueprint(forum.router)
router.register_blueprint(posts.router)

