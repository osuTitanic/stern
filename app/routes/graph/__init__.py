
from flask import Blueprint
import matplotlib as mpl

from . import activity

router = Blueprint("stats", __name__)
router.register_blueprint(activity.router)

mpl.use('agg')
