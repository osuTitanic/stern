
from app.common.database.repositories import users
from app.common.constants import Playstyle

from flask import Blueprint, request
import flask_login

router = Blueprint("playstyle", __name__)

@router.get('/playstyle/add')
@flask_login.login_required
def add_playstyle():
    if not (playstyle_name := request.args.get('type', type=str)):
        return {
            'error': 400,
            'details': 'The request is missing the required "type" parameter.'
        }, 400

    if playstyle_name not in Playstyle._member_names_:
        return {
            'error': 400,
            'details': 'The requested playstyle does not exist.'
        }, 400

    new_playstyle = Playstyle(flask_login.current_user.playstyle) | Playstyle[playstyle_name]

    users.update(
        flask_login.current_user.id,
        {'playstyle': new_playstyle.value}
    )

    return {'playstyle': new_playstyle.value}

@router.get('/playstyle/remove')
@flask_login.login_required
def remove_playstyle():
    if not (playstyle_name := request.args.get('type', type=str)):
        return {
            'error': 400,
            'details': 'The request is missing the required "type" parameter.'
        }, 400

    if playstyle_name not in Playstyle._member_names_:
        return {
            'error': 400,
            'details': 'The requested playstyle does not exist.'
        }, 400

    new_playstyle = Playstyle(flask_login.current_user.playstyle) & ~Playstyle[playstyle_name]

    users.update(
        flask_login.current_user.id,
        {'playstyle': new_playstyle.value}
    )

    return {'playstyle': new_playstyle.value}
