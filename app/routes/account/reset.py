
from app.common.database.repositories import users, verifications
from app.common import mail

from flask import Blueprint, request, redirect, abort
from typing import Optional

import flask_login
import hashlib
import config
import bcrypt
import utils
import app

router = Blueprint('reset', __name__)

def get_hashed_password(password: str) -> str:
    return bcrypt.hashpw(
        password=hashlib.md5(password.encode()) \
                        .hexdigest() \
                        .encode(),
        salt=bcrypt.gensalt()
    ).decode()

def return_to_reset_page(error: Optional[str] = None) -> str:
    return utils.render_template(
        'reset.html',
        css='account.css',
        error=error,
        title='Password Reset - Titanic!'
    )

@router.get('/reset')
def reset():
    if not flask_login.current_user.is_anonymous:
        # User has already logged in
        return redirect(f'/u/{flask_login.current_user.id}')

    return utils.render_template(
        'reset.html',
        css='account.css',
        title='Password Reset - Titanic!'
    )

@router.post('/reset')
def password_reset_request():
    if verification_token := request.form.get('token'):
        # User has entered a password on the verification page
        if not (verification := verifications.fetch_by_token(verification_token)):
            return abort(404)

        password_match = request.form.get('password_match')
        password = request.form.get('password')

        if password != password_match:
            return utils.render_template(
                'verification.html',
                css='verification.css',
                verification=verification,
                error="The passwords don't match. Please try again!",
                title="Verification - Titanic!",
                reset=True
            )

        hashed_password = get_hashed_password(password)

        users.update(
            verification.user_id,
            {'bcrypt': hashed_password}
        )

        verifications.delete(verification.token)

        app.session.logger.info(
            f'User "{verification.user_id}" successfully reset their password.'
        )

        return utils.render_template(
            'verification.html',
            css='verification.css',
            verification=verification,
            success=True,
            title="Verification - Titanic!"
        )

    if not config.EMAILS_ENABLED:
        return return_to_reset_page('Password resets are not enabled at the moment. Please contact an administrator!')

    if not (email := request.form.get('email')):
        return return_to_reset_page('Please enter a valid email!')

    if not (user := users.fetch_by_email(email)):
        return return_to_reset_page('We could not find any user with that email address.')

    app.session.logger.info('Sending verification email for resetting password...')

    verification = verifications.create(
        user.id,
        type=1,
        token_size=32
    )

    mail.send_password_reset_email(
        verification,
        user
    )

    return redirect(f'/account/verification?id={verification.id}')
