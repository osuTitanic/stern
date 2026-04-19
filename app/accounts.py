
from app.common.config import config_instance as config
from app.common.database import DBUser
from app.common.helpers import ip

from flask import Response, redirect, request
from flask_login import current_user

from . import session as app_session

import flask_login
import hashlib
import json
import secrets
import time

WEBSITE_SESSION_COOKIE_NAME = "titanic_session"

def perform_login(
    user: DBUser,
    remember: bool = True,
    response: Response | None = None
) -> Response:
    response = response or redirect(f'/u/{user.id}')

    ttl = config.FRONTEND_REFRESH_EXPIRY
    website_session = create_website_session(user.id, ttl=ttl)
    domain = resolve_domain_name()
    use_ssl = use_secure_cookies()

    response.set_cookie(
        WEBSITE_SESSION_COOKIE_NAME,
        website_session['id'],
        domain=domain,
        secure=use_ssl,
        httponly=True,
        samesite='Lax',
        max_age=ttl if remember else None
    )

    # Remove legacy authentication cookies
    expire_cookie(response, 'access_token', domain)
    expire_cookie(response, 'refresh_token', domain)
    return response

def perform_logout(response: Response | None = None) -> Response:
    domain = resolve_domain_name()
    response = response or redirect('/')

    if session_id := request.cookies.get(WEBSITE_SESSION_COOKIE_NAME):
        delete_website_session(session_id)

    expire_cookie(response, WEBSITE_SESSION_COOKIE_NAME, domain)
    flask_login.logout_user()
    return response

def create_website_session(
    user_id: int,
    now: int | None = None,
    ttl: int | None = None
) -> dict[str, int | str]:
    now = now or round(time.time())
    ttl = ttl or config.FRONTEND_REFRESH_EXPIRY
    session_id = secrets.token_hex(32)

    payload = {
        'id': session_id,
        'user_id': user_id,
        'created_at': now,
        'expires_at': now + ttl
    }
    app_session.redis.set(
        f'authentication:website:{session_id}',
        json.dumps(payload),
        ex=ttl
    )
    return payload

def validate_website_session(session_id: str) -> dict | None:
    if not session_id:
        return None

    payload = app_session.redis.get(f'authentication:website:{session_id}')

    if not payload:
        return None

    try:
        data = json.loads(payload)
    except (TypeError, ValueError):
        return

    if time.time() > data['expires_at']:
        return

    return data

def delete_website_session(session_id: str) -> None:
    if not session_id:
        return

    app_session.redis.delete(f'authentication:website:{session_id}')

def resolve_domain_name() -> str | None:
    local_domains = ('localhost', '.local')

    if any(domain in config.DOMAIN_NAME for domain in local_domains):
        return None

    if config.DEBUG:
        return None

    return f'.{config.DOMAIN_NAME}'

def use_secure_cookies() -> bool:
    return request.is_secure or not config.ALLOW_INSECURE_COOKIES

def expire_cookie(response: Response, key: str, domain: str | None = None) -> None:
    response.delete_cookie(key, domain=domain)

    if domain is not None:
        response.delete_cookie(key)

def resolve_session_identifier() -> str:
    if current_user.is_authenticated:
        return hashlib.md5(f'{current_user.id}'.encode()).hexdigest()

    user_ip = ip.resolve_ip_address_flask(request)
    return hashlib.md5(user_ip.encode()).hexdigest()
