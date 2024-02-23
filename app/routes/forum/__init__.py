
from flask import Blueprint

from . import thread
from . import post
from . import home

router = Blueprint("forum", __name__)
router.register_blueprint(thread.router)
router.register_blueprint(post.router)
router.register_blueprint(home.router)
