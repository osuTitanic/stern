
from app.common.database.repositories import users
from app.common.database import DBUser

from flask import Request, Response, redirect, request
from flask_login import current_user
from typing import Tuple, Optional
from functools import lru_cache
from werkzeug.exceptions import *

from . import accounts
from . import app

import traceback
import config
import utils

@app.login_manager.request_loader
def request_loader(request: Request):
    token = (
        request.cookies.get('access_token') or
        request.cookies.get('refresh_token')
    )

    if not token:
        return None

    data = accounts.validate_token(token)

    if not data:
        return None

    return user_loader(data['id'])

@app.flask.after_request
def refresh_access_token(response: Response) -> Response:
    if request.cookies.get('access_token'):
        return response

    if not (refresh_token := request.cookies.get('refresh_token')):
        return response

    data = accounts.validate_token(refresh_token)

    if not data:
        return response

    return accounts.perform_login(
        current_user,
        response=response
    )

@app.login_manager.user_loader
def user_loader(user_id: int) -> Optional[DBUser]:
    try:
        user = users.fetch_by_id(
            user_id,
            DBUser.groups
        )

        if not user:
            return

        return user
    except Exception as e:
        app.flask.logger.error(f'Failed to load user: {e}', exc_info=e)
        return None

@app.login_manager.unauthorized_handler
def unauthorized_user():
    return redirect(f'/account/login?redirect={request.path}')

@app.flask.errorhandler(HTTPException)
def on_http_exception(error: HTTPException) -> Tuple[str, int]:
    if utils.template_exists(f'errors/default/{error.code}.html'):
        # Use error page override for this status code
        return utils.render_error(
            code=error.code,
            description=error.description
        )

    return utils.render_template(
        template_name='errors/base.html',
        content=error.description,
        code=error.code,
        css='error.css',
        title=f'{error.name} - Titanic!'
    ), error.code

@app.flask.errorhandler(Exception)
def on_exception(error: Exception) -> Tuple[str, int]:
    traceback.print_exc()
    return utils.render_error(
        code=500,
        description='Internal Server Error'
    )

@app.flask.after_request
def set_security_headers(response: Response) -> Response:
    if not config.ENABLE_CSP:
        return response

    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=(), clipboard-write=(self)'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

static_paths = (
    '/images/arrow-white-highlight.png',
    '/images/arrow-white-normal.png',
    '/images/signup-multi.png',
    '/images/playstyles.png',
    '/images/down.gif',
    '/images/up.gif',
    '/images/achievements/',
    '/images/beatmap/',
    '/images/clients/',
    '/images/grades/',
    '/images/icons/',
    '/images/flags/',
    '/images/art/'
)

cacheable_static_paths = (
    '/js/',
    '/css/',
    '/lib/',
    '/images/',
    '/webfonts/'
)

@app.flask.after_request
def caching_rules(response: Response) -> Response:
    if config.DEBUG:
        return response

    has_static_path = any(
        request.path.startswith(path)
        for path in static_paths
    )

    if has_static_path:
        # These resources will most likely never change
        response.headers['Cache-Control'] = f'public, max-age={ 60*60*24*14 }'
        return response

    has_static_path = any(
        request.path.startswith(path)
        for path in cacheable_static_paths
    )

    if not has_static_path:
        return response

    if not request.args.get('c'):
        return response

    response.headers['Cache-Control'] = f'public, max-age={ 60*60*24*7 }'
    return response
