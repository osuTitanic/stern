

from flask import Blueprint, redirect
from typing import Optional

from . import stats
from . import home

router = Blueprint("routes", __name__)
router.register_blueprint(stats.router, url_prefix='/stats')
router.register_blueprint(home.router, url_prefix='/')

@router.get('/index')
@router.get('/index<extension>')
def index(extension: Optional[str] = None):
    return redirect('/')
