
from app.common.config import config_instance as config
from flask import Blueprint, redirect

from . import account
from . import public
from . import forum

router = Blueprint("routes", __name__)
router.register_blueprint(account.router, url_prefix='/account')
router.register_blueprint(forum.router, url_prefix='/forum')
router.register_blueprint(public.router, url_prefix='/')

@router.get("/api/<path>")
def api_redirect(path: str):
    return redirect(f"{config.API_BASEURL}/{path}", code=308)
