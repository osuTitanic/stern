
from flask import Blueprint

from . import account
from . import public
from . import forum
from . import api

router = Blueprint("routes", __name__)
router.register_blueprint(account.router, url_prefix='/account')
router.register_blueprint(forum.router, url_prefix='/forum')
router.register_blueprint(api.router, url_prefix='/api')
router.register_blueprint(public.router, url_prefix='/')
