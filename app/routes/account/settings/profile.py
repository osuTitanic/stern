
from flask_login import login_required
from flask import Blueprint

from . import avatar

import utils

router = Blueprint('profile-settings', __name__)
router.register_blueprint(avatar.router, url_prefix='/profile')

@router.get('/profile')
@login_required
def profile_settings():
    return utils.render_template(
        'settings/profile.html',
        css='settings.css'
    )
