
from flask import Blueprint, redirect, request
from flask_login import login_required
from typing import Optional

from app.common.database.repositories import verifications
from app.common.database.repositories import users
from app.common import mail

import flask_login
import hashlib
import bcrypt
import utils
import app

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
    with app.session.database.managed_session() as session:
        if not (current_password := request.form.get('current-password')):
            return get_profile_page(error='Please enter your current password!')

        md5_password = hashlib.md5(
            current_password.encode()
        ).hexdigest()

        if not bcrypt.checkpw(md5_password.encode(), flask_login.current_user.bcrypt.encode()):
            return get_profile_page(error='Your password was incorrect. Please try again!')

        new_email = request.form.get('new-email')
        email_confirm = request.form.get('email-confirm')

        if new_email and email_confirm:
            if new_email != email_confirm:
                return get_profile_page(
                    error="The emails don't match. Please try again!"
                )

            if users.fetch_by_email(new_email.lower(), session=session):
                return get_profile_page(
                    error="There already is a user with that email. Please choose another one, or reset your password!"
                )

            mail.send_email_changed(flask_login.current_user)

            users.update(
                flask_login.current_user.id,
                {
                    'activated': False,
                    'email': new_email.lower()
                },
                session=session
            )

            verification = verifications.create(
                flask_login.current_user.id,
                type=0,
                session=session
            )

            flask_login.current_user.email = new_email
            mail.send_reactivate_account_email(
                verification,
                flask_login.current_user
            )

            flask_login.logout_user()

            return redirect(f'/account/verification?id={verification.id}')

        new_password = request.form.get('new-password')
        password_confirm = request.form.get('password-confirm')

        if new_password and password_confirm:
            if new_password != password_confirm:
                return get_profile_page(error="The passwords don't match. Please try again!")

            hashed_password = bcrypt.hashpw(
                hashlib.md5(new_password.encode()) \
                    .hexdigest() \
                    .encode(),
                bcrypt.gensalt()
            ).decode()

            users.update(flask_login.current_user.id, {'bcrypt': hashed_password}, session=session)
            mail.send_password_changed_email(flask_login.current_user)

            return get_profile_page(info='Your password was updated.')

        return redirect('/account/settings/profile')
