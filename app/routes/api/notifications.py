
from app.common.database.repositories import notifications
from flask import Blueprint, Response, request

import flask_login

router = Blueprint('notifications', __name__)

@router.get('/confirm')
@flask_login.login_required
def mark_as_read():
    if (id := request.args.get('id')) is None:
        return Response(None, 400)

    if not notifications.update(id, {'read': True}):
        return Response(None, 404)

    return Response(None, 200)
