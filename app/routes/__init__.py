

from flask import Blueprint

from . import stats
from . import home

router = Blueprint("routes", __name__)
router.register_blueprint(stats.router, url_prefix='/stats')
router.register_blueprint(home.router, url_prefix='/')

