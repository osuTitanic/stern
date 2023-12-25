
from app.common.database.repositories import users
from app.common.constants import Playstyle

from flask import Blueprint, Response, request
import flask_login
import json

router = Blueprint("playstyle", __name__)

@router.get('/playstyle/add')
@flask_login.login_required
def add_playstyle():
    if not (playstyle_name := request.args.get('type', type=str)):
        return Response(
            response=(),
            status=400,
            mimetype='application/json'
        )

    if playstyle_name not in Playstyle._member_names_:
        return Response(
            response=(),
            status=400,
            mimetype='application/json'
        )

    new_playstyle = Playstyle(flask_login.current_user.playstyle) | Playstyle[playstyle_name]

    users.update(
        flask_login.current_user.id,
        {'playstyle': new_playstyle.value}
    )

    return Response(
        response=json.dumps({'playstyle': new_playstyle.value}),
        status=200,
        mimetype='application/json'
    )

@router.get('/playstyle/remove')
@flask_login.login_required
def remove_playstyle():
    if not (playstyle_name := request.args.get('type', type=str)):
        return Response(
            response=(),
            status=400,
            mimetype='application/json'
        )

    if playstyle_name not in Playstyle._member_names_:
        return Response(
            response=(),
            status=400,
            mimetype='application/json'
        )

    new_playstyle = Playstyle(flask_login.current_user.playstyle) & ~Playstyle[playstyle_name]

    users.update(
        flask_login.current_user.id,
        {'playstyle': new_playstyle.value}
    )

    return Response(
        response=json.dumps({'playstyle': new_playstyle.value}),
        status=200,
        mimetype='application/json'
    )
