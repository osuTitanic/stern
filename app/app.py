
from app.common.database.repositories import users
from app.common.database import DBUser

from flask import Flask, Request, Response, jsonify, redirect, request, session
from flask_pydantic.exceptions import ValidationError
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from flask_squeeze import Squeeze
from typing import Tuple, Optional
from werkzeug.exceptions import *

from . import accounts
from . import common
from . import routes
from . import bbcode

import traceback
import config
import utils

flask = Flask(
    __name__,
    static_url_path='',
    static_folder='static',
    template_folder='templates'
)

csrf = CSRFProtect()
csrf.init_app(flask)

login_manager = LoginManager()
login_manager.init_app(flask)

flask.register_blueprint(routes.router)
flask.secret_key = config.FRONTEND_SECRET_KEY
flask.config['FLASK_PYDANTIC_VALIDATION_ERROR_RAISE'] = True

if not config.DEBUG:
    minify = Squeeze()
    minify.init_app(flask)

@login_manager.request_loader
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

@flask.after_request
def refresh_access_token(response: Response) -> Response:
    if request.cookies.get('access_token'):
        return response

    if "_user_id" in session:
        return accounts.perform_login_migration(response)
    
    if not (refresh_token := request.cookies.get('refresh_token')):
        return response

    data = accounts.validate_token(refresh_token)

    if not data:
        return response

    return accounts.perform_login(
        current_user,
        response=response
    )

@flask.after_request
def caching_rules(response: Response) -> Response:
    if config.DEBUG:
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

    has_static_path = any(
        request.path.startswith(path)
        for path in static_paths
    )

    if has_static_path:
        # These resources will most likely never change
        response.headers['Cache-Control'] = f'public, max-age={ 60*60*24*14 }'
        return response

    commit_static_paths = (
        '/js/',
        '/css/',
        '/lib/',
        '/images/',
        '/webfonts/'
    )

    has_static_path = any(
        request.path.startswith(path)
        for path in commit_static_paths
    )

    if not has_static_path:
        return response

    if not request.args.get('commit'):
        return response

    response.headers['Cache-Control'] = f'public, max-age={ 60*60*24*7 }'
    return response

@login_manager.user_loader
def user_loader(user_id: int) -> Optional[DBUser]:
    try:
        user = users.fetch_by_id(
            user_id,
            DBUser.groups,
            DBUser.relationships
        )

        if not user:
            return

        return user
    except Exception as e:
        flask.logger.error(f'Failed to load user: {e}', exc_info=e)
        return None

@login_manager.unauthorized_handler
def unauthorized_user():
    if request.path.startswith('/api'):
        return jsonify(
            error=403,
            details='You are not authorized to perform this action.'
        ), 403

    return redirect(f'/account/login?redirect={request.path}')

@flask.errorhandler(HTTPException)
def on_http_exception(error: HTTPException) -> Tuple[str, int]:
    if request.path.startswith('/api'):
        return jsonify(
            error=error.code,
            details=error.description or error.name
        ), error.code

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

@flask.errorhandler(Exception)
def on_exception(error: Exception) -> Tuple[str, int]:
    traceback.print_exc()

    if request.path.startswith('/api'):
        return jsonify(
            error=500,
            details=InternalServerError.description
        ), 500

    return utils.render_error(500, description='Internal Server Error')

@flask.errorhandler(ValidationError)
def on_validation_error(error: ValidationError) -> Tuple[str, int]:
    params = {
        param: getattr(error, param)
        for param in (
            'body_params',
            'form_params',
            'path_params',
            'query_params'
        )
    }

    return jsonify(
        error=400,
        details={
            'validation_error': {
                name: value
                for name, value in params.items()
                if value is not None
            }
        }
    ), 400
