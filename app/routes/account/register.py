
from app.common.constants.regexes import USERNAME, EMAIL
from app.common.constants import NotificationType
from app.common.helpers.external import location
from app.common import mail, officer, helpers
from app.common.database.repositories import (
    verifications,
    notifications,
    groups,
    names,
    users
)

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
        error=error,
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
    username = username.strip()

    if len(username) < 3:
        return "Your username is too short."

    if len(username) > 25:
        return "Your username is too long."

    if not USERNAME.match(username):
        return "Your username contains invalid characters."

    safe_name = username.lower().replace(' ', '_')

    if users.fetch_by_safe_name(safe_name):
        return "This username is already in use!"

    if names.fetch_by_name_extended(username):
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
        title='Register - osu!Titanic',
        site_title='Register',
        site_description='Create your account and start playing today!'
    )

@router.post('/register')
def registration_request():
    ip = helpers.ip.resolve_ip_address_flask(request)

    try:
        if validate_email(email := request.form.get('email')):
            return return_to_register_page('Please enter a valid email!')

        if validate_username(username := request.form.get('username')):
            return return_to_register_page('Please enter a valid username!')

        if not (password := request.form.get('password')):
            return return_to_register_page('Please enter a valid password!')

        if len(password) <= 7:
            return return_to_register_page('Please enter a password with at least 8 characters!')
    except Exception as e:
        app.session.logger.error(
            f'Failed to verify registration request: {e}',
            exc_info=e
        )
        officer.call(
            f'Failed to verify registration request from IP ({ip}): {e}',
            exc_info=e
        )
        return return_to_register_page('Failed to process your request. Please try again!')

    registration_count = app.session.redis.get(f'registrations:{ip}') or 0

    if int(registration_count) > 2:
        officer.call(
            f'Failed to register: Too many registrations from IP ({ip})'
        )
        return return_to_register_page('There have been too many registrations from this ip. Please try again later!')

    app.session.logger.info(
        f'Starting registration process for "{username}" ({email}) ({ip})...'
    )

    geolocation = location.fetch_web(ip)
    country = geolocation.country_code.upper() if geolocation else 'XX'

    cf_country = request.headers.get('CF-IPCountry')

    if cf_country != None and cf_country not in ('XX', 'T1'):
        country = cf_country.upper()

    hashed_password = get_hashed_password(password)
    username = username.strip()
    safe_name = username.lower().replace(' ', '_')

    user = users.create(
        username=username,
        safe_name=safe_name,
        email=email.lower(),
        pw_bcrypt=hashed_password,
        country=country,
        activated=False if config.EMAILS_ENABLED else True,
        permissions=5
    )

    if not user:
        officer.call(f'Failed to register user "{username}".')
        return return_to_register_page('An error occured on the server side. Please try again!')

    app.session.logger.info(f'User "{username}" with id "{user.id}" was created.')

    # Send welcome notification
    notifications.create(
        user.id,
        NotificationType.Welcome.value,
        'Welcome!',
        'Welcome aboard! '
        f'Get started by downloading one of our builds [here](https://osu.{config.DOMAIN_NAME}/download). '
        'Enjoy your journey!'
    )

    # Add user to players & supporters group
    groups.create_entry(user.id, 999)
    groups.create_entry(user.id, 1000)

    # Increment registration count
    app.session.redis.incr(f'registrations:{ip}')
    app.session.redis.expire(f'registrations:{ip}', 3600 * 24)

    if not config.EMAILS_ENABLED:
        # Verification is disabled
        flask_login.login_user(user)
        app.session.logger.info('Registration finished.')
        return redirect(f'/u/{user.id}')

    app.session.logger.info('Sending verification email...')

    verification = verifications.create(
        user.id,
        type=0,
        token_size=32
    )

    mail.send_welcome_email(
        verification,
        user
    )

    app.session.logger.info('Registration finished.')

    return redirect(f'/account/verification?id={verification.id}')

@router.get('/register/check')
def input_validation():
    if not (type := request.args.get('type')):
        return ''

    if not (value := request.args.get('value')):
        return ''

    return {
        'username': validate_username,
        'email': validate_email
    }[type](value) or ''
