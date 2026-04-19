
from app.common.config import config_instance as config
from app.common.database import DBUser
from app.common.helpers import ip

from flask import Response, g, redirect, request
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

    website_session = create_session(
        user.id,
        ttl=ttl,
        remember=remember
    )
    set_session_cookie(
        response,
        website_session['id'],
        remember,
        ttl
    )
    return response

def perform_logout(response: Response | None = None) -> Response:
    domain = resolve_domain_name()
    response = response or redirect('/')

    if session_id := request.cookies.get(WEBSITE_SESSION_COOKIE_NAME):
        delete_session(session_id)

    expire_cookie(response, WEBSITE_SESSION_COOKIE_NAME, domain)
    flask_login.logout_user()
    return response

def create_session(
    user_id: int,
    now: int | None = None,
    ttl: int | None = None,
    remember: bool = True
) -> dict[str, int | str | bool]:
    now = now or round(time.time())
    ttl = ttl or config.FRONTEND_REFRESH_EXPIRY
    session_id = secrets.token_hex(32)

    payload = {
        'id': session_id,
        'user_id': user_id,
        'created_at': now,
        'expires_at': now + ttl,
        'remember': remember
    }
    persist_session(payload, ttl)
    return payload

def validate_session(session_id: str) -> dict | None:
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

def should_refresh_session(
    data: dict,
    now: int | None = None
) -> bool:
    if 'remember' not in data:
        return False

    threshold = min(
        config.FRONTEND_SESSION_REFRESH_THRESHOLD,
        config.FRONTEND_REFRESH_EXPIRY
    )

    if threshold <= 0:
        return False

    now = now or round(time.time())
    remaining_ttl = data['expires_at'] - now
    return remaining_ttl <= threshold

def queue_session_refresh(
    data: dict,
    now: int | None = None
) -> None:
    if getattr(g, 'website_session_refresh', None):
        return

    now = now or round(time.time())
    ttl = config.FRONTEND_REFRESH_EXPIRY

    # Store session data in flask context for later use in response handler
    g.website_session_refresh = {
        'id': data['id'],
        'user_id': data['user_id'],
        'created_at': data['created_at'],
        'expires_at': now + ttl,
        'remember': bool(data['remember'])
    }

def refresh_session(response: Response) -> Response:
    # Called after request processing
    # If we have session data queued for refresh, persist it & set a new cookie
    if not (data := getattr(g, 'website_session_refresh', None)):
        return response

    ttl = config.FRONTEND_REFRESH_EXPIRY
    persist_session(data, ttl)
    set_session_cookie(response, data['id'], bool(data['remember']), ttl)
    return response

def delete_session(session_id: str) -> None:
    app_session.redis.delete(f'authentication:website:{session_id}')

def persist_session(payload: dict[str, int | str | bool], ttl: int) -> None:
    app_session.redis.set(
        f'authentication:website:{payload["id"]}',
        json.dumps(payload),
        ex=ttl
    )

def resolve_domain_name() -> str | None:
    local_domains = ('localhost', '.local')

    if any(domain in config.DOMAIN_NAME for domain in local_domains):
        return None

    if config.DEBUG:
        return None

    return f'.{config.DOMAIN_NAME}'

def use_secure_cookies() -> bool:
    return request.is_secure or not config.ALLOW_INSECURE_COOKIES

def set_session_cookie(
    response: Response,
    session_id: str,
    remember: bool,
    ttl: int
) -> None:
    domain = resolve_domain_name()
    use_ssl = use_secure_cookies()

    response.set_cookie(
        WEBSITE_SESSION_COOKIE_NAME,
        session_id,
        domain=domain,
        secure=use_ssl,
        httponly=True,
        samesite='Lax',
        max_age=ttl if remember else None
    )

def expire_cookie(response: Response, key: str, domain: str | None = None) -> None:
    response.delete_cookie(key, domain=domain)

    if domain is not None:
        response.delete_cookie(key)

def resolve_session_identifier() -> str:
    if current_user.is_authenticated:
        return hashlib.md5(f'{current_user.id}'.encode()).hexdigest()

    user_ip = ip.resolve_ip_address_flask(request)
    return hashlib.md5(user_ip.encode()).hexdigest()
