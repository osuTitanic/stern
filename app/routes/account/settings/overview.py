
from app.common.database.repositories import logins

from flask_login import login_required
from flask import Blueprint

import flask_login
import utils

router = Blueprint('overview', __name__)

@router.get('/')
@login_required
def settings_overview():
    return utils.render_template(
        'settings/overview.html',
        css='settings.css',
        logins=logins.fetch_many(
           flask_login.current_user.id,
           limit=5
        )
    )
