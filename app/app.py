
from app.common.database import DBUser, DBForum, DBForumTopic
from app.common.database.repositories import users

from flask import Flask, Request, jsonify, redirect, request
from flask_pydantic.exceptions import ValidationError
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from typing import Tuple, Optional
from werkzeug.exceptions import *

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

flask.register_blueprint(routes.router)
flask.secret_key = config.FRONTEND_SECRET_KEY
flask.config['FLASK_PYDANTIC_VALIDATION_ERROR_RAISE'] = True

login_manager = LoginManager()
login_manager.init_app(flask)

csrf = CSRFProtect()
csrf.init_app(flask)

@flask.errorhandler(HTTPException)
def on_http_exception(error: HTTPException) -> Tuple[str, int]:
    if '/api' in request.base_url:
        return jsonify(
            error=error.code,
            details=error.description or error.name
        ), error.code

    custom_description = getattr(
        error,
        'html_description',
        error.description or error.name
    )

    if error.description.startswith('<'):
        # Okay, I know this solution is bad, but I'm
        # too lazy to find a better one right now.
        custom_description = error.description

    return utils.render_template(
        content=custom_description,
        code=error.code,
        template_name='error.html',
        css='error.css',
        title=f'{error.name} - Titanic!'
    ), error.code

@flask.errorhandler(Exception)
def on_exception(error: Exception) -> Tuple[str, int]:
    traceback.print_exc()

    if '/api' in request.base_url:
        return jsonify(
            error=500,
            details=InternalServerError.description
        ), 500

    return utils.render_template(
        content=InternalServerError.html_description,
        code=500,
        template_name='error.html',
        css='error.css',
        title=f'Internal Server Error - Titanic!'
    ), 500

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

@login_manager.request_loader
def request_loader(request: Request):
    user_id = request.form.get('id')
    return user_loader(user_id)

@login_manager.unauthorized_handler
def unauthorized_user():
    if request.path.startswith('/api'):
        return jsonify(
            error=403,
            details='You are not authorized to perform this action.'
        ), 403

    return redirect('/?login=True')
