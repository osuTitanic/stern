
from flask_login import login_required
from flask import Blueprint

import utils

router = Blueprint('profile-settings', __name__)

@router.get('/profile')
@login_required
def profile_settings():
    return utils.render_template(
        'settings/profile.html',
        css='settings.css'
    )
