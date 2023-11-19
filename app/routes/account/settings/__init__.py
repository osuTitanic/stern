
from flask import Blueprint

from . import overview
from . import profile

router = Blueprint('settings', __name__)
