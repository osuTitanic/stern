
from flask import Blueprint

from . import forum
from . import topic
from . import post
from . import home

router = Blueprint("forum", __name__)
router.register_blueprint(forum.router)
router.register_blueprint(topic.router)
router.register_blueprint(post.router)
router.register_blueprint(home.router)
