
from app.common.database.repositories import users

from flask import Blueprint, request, redirect
from flask_login import login_required

from . import account
from . import avatar

import flask_login
import utils
import app

router = Blueprint('profile-settings', __name__)
router.register_blueprint(account.router, url_prefix='/profile')
router.register_blueprint(avatar.router, url_prefix='/profile')

@router.get('/profile')
@login_required
def profile_settings():
    return utils.render_template(
        'settings/profile.html',
        css='settings.css'
    )

@router.post('/profile/userpage')
@login_required
def update_userpage():
    if not (bbcode := request.form.get('bbcode')):
        return redirect('/account/settings/profile')

    try:
        users.update(
            flask_login.current_user.id,
            {'userpage_about': bbcode}
        )
    except Exception as e:
        app.session.logger.error(
            f'Failed to update userpage: {e}',
            exc_info=e
        )
        return utils.render_template(
            'settings/profile.html',
            css='settings.css',
            error="Failed to update userpage!"
        )

    return utils.render_template(
        'settings/profile.html',
        css='settings.css',
        info="Successfully updated userpage."
    )
