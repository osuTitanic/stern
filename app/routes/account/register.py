
from app.common.config import config_instance as config
from app.common.constants import NotificationType, UserActivity
from app.common.constants.country import COUNTRIES as Countries
from app.common.constants.regexes import USERNAME, EMAIL
from app.common.constants.strings import BAD_WORDS
from app.common.helpers.external import location
from app.common import mail, officer, helpers
from app.common.helpers import activity
from app.common.database.repositories import (
    verifications,
    notifications,
    wrapper,
    groups,
    names,
    users
)

from flask import Blueprint, request, redirect
from sqlalchemy.orm import Session
from typing import Optional
from app import accounts

import flask_login
import hashlib
import bcrypt
import utils
import app

router = Blueprint('register', __name__)

@router.get('/register')
def register_page():
    if not flask_login.current_user.is_anonymous:
        # User has already logged in
        return redirect(f'/u/{flask_login.current_user.id}')

    return render_register_page()

@router.post('/register')
def registration_request():
    with app.session.database.managed_session() as session:
        ip = helpers.ip.resolve_ip_address_flask(request)

        try:
            if validate_email(email := request.form.get('email'), session=session):
                return render_register_page('Please enter a valid email!')

            if validate_username(username := request.form.get('username'), session=session):
                return render_register_page('Please enter a valid username!')

            if not (password := request.form.get('password')):
                return render_register_page('Please enter a valid password!')

            if len(password) <= 7:
                return render_register_page('Please enter a password with at least 8 characters!')
        except Exception as e:
            app.session.logger.error(
                f'Failed to verify registration request: {e}',
                exc_info=e
            )
            officer.call(
                f'Failed to verify registration request from IP ({ip}): {e}',
                exc_info=e
            )
            return render_register_page('Failed to process your request. Please try again!')

        registration_count = app.session.redis.get(f'registrations:{ip}') or 0

        if int(registration_count) > 2:
            officer.call(
                f'Failed to register: Too many registrations from IP ({ip})'
            )
            return render_register_page('There have been too many registrations from this ip. Please try again later!')

        if config.RECAPTCHA_SECRET_KEY and config.RECAPTCHA_SITE_KEY:
            client_response = request.form.get('recaptcha_response')

            if not client_response:
                return render_register_page('Invalid captcha response!')

            response = app.session.requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data={
                    'secret': config.RECAPTCHA_SECRET_KEY,
                    'response': client_response,
                    'remoteip': ip
                }
            )

            if not response.ok:
                return render_register_page('Failed to verify captcha response!')

            if not response.json().get('success', False):
                return render_register_page('Captcha verification failed!')

        app.session.logger.info(
            f'Starting registration process for "{username}" ({email}) ({ip})...'
        )

        geolocation = location.fetch_web(ip)
        country = geolocation.country_code.upper() if geolocation else 'XX'

        # Force-override country if cloudflare geolocation is available
        cf_country = request.headers.get('CF-IPCountry', 'XX')

        if cf_country not in ('XX', 'T1'):
            country = cf_country.upper()

        if country not in Countries:
            country = 'XX'
            officer.call(f'Unknown country code "{country}" ({ip})')

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
            session=session
        )

        if not user:
            officer.call(f'Failed to register user "{username}".')
            return render_register_page('An error occured on the server side. Please try again!')

        app.session.logger.info(f'User "{username}" with id "{user.id}" was created.')
        officer.call(f'New user registration: "[{username}]({config.OSU_BASEURL}/u/{user.id})" ({ip})')

        # Broadcast user registration
        activity.submit(
            user.id, None,
            UserActivity.UserRegistration,
            {'username': user.name},
            is_hidden=True,
            session=session
        )
    
        # Send welcome notification
        notifications.create(
            user.id,
            NotificationType.Welcome.value,
            'Welcome!',
            'Welcome aboard! '
            f'Get started by downloading one of our builds [here]({config.OSU_BASEURL}/download). '
            'Enjoy your journey!',
            session=session
        )

        # Add user to players & supporters group
        groups.create_entry(user.id, 999, session=session)
        groups.create_entry(user.id, 1000, session=session)

        # Increment registration count
        app.session.redis.incr(f'registrations:{ip}')
        app.session.redis.expire(f'registrations:{ip}', 3600 * 24)

        if not config.EMAILS_ENABLED:
            # Verification is disabled
            app.session.logger.info('Registration finished.')
            return accounts.perform_login(user)

        app.session.logger.info('Sending verification email...')

        verification = verifications.create(
            user.id,
            type=0,
            token_size=32,
            session=session
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

    validators = {
        'username': validate_username,
        'email': validate_email
    }

    if not (validator := validators.get(type)):
        return ''

    return validator(value) or ''

def render_register_page(error: Optional[str] = None) -> str:
    return utils.render_template(
        'register.html',
        css='account.css',
        title='Register - Titanic!',
        site_title='Register',
        site_description='Create your account and start playing today!',
        site_image=f"{app.config.OSU_BASEURL}/images/logo/main-low.png",
        error=error
    )

def get_hashed_password(password: str) -> str:
    return bcrypt.hashpw(
        password=hashlib.md5(password.encode()) \
                        .hexdigest() \
                        .encode(),
        salt=bcrypt.gensalt()
    ).decode()

@wrapper.session_wrapper
def validate_username(username: str, session: Session = ...) -> Optional[str]:
    username = username.strip()

    if len(username) < 3:
        return "Your username is too short."

    if len(username) > 15:
        return "Your username is too long."

    if not USERNAME.match(username):
        return "Your username contains invalid characters."

    if any(word in username.lower() for word in BAD_WORDS):
        return "Your username contains offensive words."

    if username.lower().startswith('deleteduser'):
        return "This username is not allowed."

    if username.lower().endswith('_old'):
        return "This username is not allowed."

    if users.fetch_by_name_case_insensitive(username, session):
        return "This username is already in use!"

    safe_name = username.lower().replace(' ', '_')

    if users.fetch_by_safe_name(safe_name, session):
        return "This username is already in use!"

    if names.fetch_by_name_reserved(username, session):
        return "This username is already in use!"

@wrapper.session_wrapper
def validate_email(email: str, session: Session = ...) -> Optional[str]:
    if not EMAIL.match(email):
        return "Please enter a valid email address!"

    if users.fetch_by_email(email.lower(), session):
        # TODO: Forgot username/password link
        return "This email address is already in use."
