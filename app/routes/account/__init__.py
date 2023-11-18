
from flask import Blueprint

from . import verification
from . import register
from . import logout
from . import login

router = Blueprint('account', __name__)
router.register_blueprint(verification.router)
router.register_blueprint(register.router)
router.register_blueprint(logout.router)
router.register_blueprint(login.router)
