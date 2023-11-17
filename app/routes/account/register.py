
from app.common.constants.regexes import USERNAME, EMAIL
from app.common.database.repositories import users

from flask import Blueprint, request, redirect
from typing import Optional

import flask_login
import hashlib
import config
import bcrypt
import utils
import app

router = Blueprint('register', __name__)

def return_to_register_page(error: Optional[str] = None) -> str:
    return utils.render_template(
        'register.html',
        css='register.css',
        error=error, # TODO: Error feedback
        title='Register - osu!Titanic'
    )

def get_hashed_password(password: str) -> str:
    return bcrypt.hashpw(
        password=hashlib.md5(password.encode()) \
                        .hexdigest() \
                        .encode(),
        salt=bcrypt.gensalt()
    ).decode()

def validate_username(username: str) -> Optional[str]:
    if len(username) < 3:
        return "Your username is too short."

    if len(username) > 15:
        return "Your username is too long."

    if not USERNAME.match(username):
        return "Your username contains invalid characters."

    if users.fetch_by_safe_name(username.lower()):
        return "This username is already in use!"

def validate_email(email: str) -> Optional[str]:
    if not EMAIL.match(email):
        return "Please enter a valid email address!"

    if users.fetch_by_email(email.lower()):
        # TODO: Forgot username/password link
        return "This email address is already in use."

@router.get('/register')
def register():
    if not flask_login.current_user.is_anonymous:
        # User has already logged in
        return redirect(f'/u/{flask_login.current_user.id}')

    return utils.render_template(
        'register.html',
        css='register.css',
        title='Register - osu!Titanic'
    )

@router.post('/register')
def registration_request():
    redirect_url = request.form.get('redirect', '/')

    try:
        if validate_email(email := request.form.get('email')):
            return return_to_register_page('email')

        if validate_username(username := request.form.get('username')):
            return return_to_register_page('username')

        if not (password := request.form.get('password')):
            return return_to_register_page('password')
    except Exception as e:
        app.session.logger.error(
            f'Failed to verify registration request: {e}',
            exc_info=e
        )
        return return_to_register_page('validation')

    # TODO: Check for ip bans

    app.session.logger.info(
        f'Starting registration process for "{username}" ({email})...'
    )

    hashed_password = get_hashed_password(password)
    safe_name = username.lower() \
                        .replace(' ', '_')

    user = users.create(
        username=username,
        safe_name=safe_name,
        email=email,
        pw_bcrypt=hashed_password,
        country='XX', # TODO: Get country via. IP
        activated=False,
        permissions=1 if not config.FREE_SUPPORTER else 5
    )

    if not user:
        app.session.logger.warning(f'Failed to register user "{username}".')
        return return_to_register_page('server')

    app.session.logger.info(f'User "{username}" with id "{user.id}" was created.')
    app.session.logger.info('Registration finished.')

    return redirect(redirect_url)

@router.get('/register/check')
def input_validation():
    if not (type := request.args.get('type')):
        return

    if not (value := request.args.get('value')):
        return

    return {
        'username': validate_username,
        'email': validate_email
    }[type](value) or ''
