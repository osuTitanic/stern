
from app.common.database.repositories import notifications
from flask_login import login_required
from flask import Blueprint, request

router = Blueprint('notifications', __name__)

@router.get('/confirm')
@login_required
def mark_as_read():
    if (id := request.args.get('id')) is None:
        return {
            'error': 400,
            'details': 'The request is missing the required "id" parameter.'
        }, 400

    if not notifications.update(id, {'read': True}):
        return {
            'error': 404,
            'details': 'The requested notification does not exist.'
        }, 404

    return {'success': True}
