
from flask import Blueprint, redirect, request
from flask_login import login_required
from typing import Optional

import flask_login
import hashlib
import bcrypt
import utils
import app
import io

router = Blueprint('account-settings', __name__)

def get_profile_page(error: Optional[str] = None, info: Optional[str] = None):
    return utils.render_template(
        'settings/profile.html',
        css='settings.css',
        error=error,
        info=info
    )

@router.get('/edit')
@login_required
def redirect_to_settings():
    return redirect('/account/settings/profile')

@router.post('/edit')
@login_required
def edit_account_info():
    if not (current_password := request.args.get('current-password')):
        return get_profile_page(error='Please enter your current password!')

    md5_password = hashlib.md5(
        current_password.encode()
    ).hexdigest()

    if not bcrypt.checkpw(md5_password.encode(), flask_login.current_user.bcrypt.encode()):
        return get_profile_page(error='Your password was incorrect. Please try again!')

    # TODO: ...

    return redirect('/account/settings/profile')
