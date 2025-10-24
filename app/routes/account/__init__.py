
from flask import Blueprint, redirect

from . import verification
from . import register
from . import overview
from . import security
from . import friends
from . import profile
from . import logout
from . import login
from . import reset
from . import chat

router = Blueprint('account', __name__)
router.register_blueprint(verification.router)
router.register_blueprint(register.router)
router.register_blueprint(overview.router)
router.register_blueprint(security.router)
router.register_blueprint(profile.router)
router.register_blueprint(friends.router)
router.register_blueprint(logout.router)
router.register_blueprint(login.router)
router.register_blueprint(reset.router)
router.register_blueprint(chat.router)

@router.get("/settings")
@router.get("/settings/")
@router.get("/settings/<path>")
def settings_redirect(path: str = ""):
    # Redirect old /settings routes -> /account routes
    return redirect(f'/account/{path}')
