
from app.common.config import config_instance as config
from app.common.constants import TokenSource
from app.common.database import DBUser

from flask import Response, redirect, request, session as flask_session
from flask_login import current_user

import flask_login
import secrets
import hashlib
import time
import jwt

def perform_login(
    user: DBUser,
    remember: bool = True,
    response: Response | None = None
) -> Response:
    response = response or redirect(f'/u/{user.id}')

    current_time = round(time.time())
    expiry = current_time + config.FRONTEND_TOKEN_EXPIRY
    expiry_refresh = current_time + config.FRONTEND_REFRESH_EXPIRY

    access_token = generate_token(user, expiry, TokenSource.Web)
    refresh_token = generate_token(user, expiry_refresh, TokenSource.Web)

    domain = resolve_domain_name()
    use_ssl = request.is_secure or not config.ALLOW_INSECURE_COOKIES

    response.set_cookie(
        'access_token',
        access_token,
        domain=domain,
        secure=use_ssl,
        httponly=domain is not None,
        max_age=config.FRONTEND_TOKEN_EXPIRY
    )

    if remember:
        response.set_cookie(
            'refresh_token',
            refresh_token,
            domain=domain,
            secure=use_ssl,
            httponly=domain is not None,
            max_age=config.FRONTEND_REFRESH_EXPIRY
        )

    return response

def perform_logout(response: Response | None = None) -> Response:
    domain = resolve_domain_name()
    response = response or redirect('/')
    response.delete_cookie('access_token', domain=domain)
    response.delete_cookie('refresh_token', domain=domain)
    flask_login.logout_user()
    return response

def generate_token(user: DBUser, expiry: int, source=TokenSource.Web) -> str:
    return jwt.encode(
        {
            'id': user.id,
            'name': user.name,
            'exp': expiry,
            'source': source.value
        },
        config.FRONTEND_SECRET_KEY,
        algorithm='HS256'
    )

def validate_token(token: str) -> dict | None:
    try:
        data = jwt.decode(
            token,
            config.FRONTEND_SECRET_KEY,
            algorithms=['HS256']
        )
    except jwt.PyJWTError:
        return

    # Check if the token is expired
    if time.time() > data['exp']:
        return

    return data

def resolve_domain_name() -> str | None:
    local_domains = ('localhost', '.local')
    
    if any(domain in config.DOMAIN_NAME for domain in local_domains):
        return None

    if config.DEBUG:
        return None

    return f'.{config.DOMAIN_NAME}'

def resolve_session_identifier() -> str:
    if current_user.is_authenticated:
        return hashlib.md5(f'{current_user.id}'.encode()).hexdigest()

    if 'session_id' not in flask_session:
        flask_session['session_id'] = secrets.token_hex(16)

    return hashlib.md5(flask_session['session_id'].encode()).hexdigest()
