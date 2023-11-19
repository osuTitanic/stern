
from flask_login import login_required
from flask import Blueprint

import utils

router = Blueprint('overview', __name__)

@router.get('/')
@login_required
def settings_overview():
    return utils.render_template(
        'settings/overview.html',
        css='settings.css'
    )
