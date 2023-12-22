
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

@router.post('/profile')
@login_required
def update_profile_settings():
    interests = request.form.get('interests') or None
    location = request.form.get('location') or None
    website = request.form.get('website') or None
    discord = request.form.get('discord') or None
    twitter = request.form.get('twitter') or None

    users.update(
        flask_login.current_user.id,
        {
            'userpage_interests': interests,
            'userpage_location': location,
            'userpage_website': website,
            'userpage_discord': discord,
            'userpage_twitter': f'https://twitter.com/{app.get_handle(twitter)}' \
                if twitter else None
        }
    )

    return utils.render_template(
        'settings/profile.html',
        css='settings.css',
        info='Successfully updated profile.'
    )

@router.post('/profile/userpage')
@login_required
def update_userpage():
    if (bbcode := request.form.get('bbcode')) is None:
        return redirect('/account/settings/profile')

    users.update(
        flask_login.current_user.id,
        {'userpage_about': bbcode}
    )

    return redirect('/account/settings/profile#userpage')
