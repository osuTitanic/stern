
from app.common.database.repositories import notifications
from flask_login import login_required, current_user
from flask import Blueprint, request

router = Blueprint('notifications', __name__)

@router.get('/confirm/all')
@login_required
def mark_all_as_read():
    notifications.update_by_user_id(
        current_user.id,
        {'read': True}
    )
    return {'success': True}

@router.get('/confirm')
@login_required
def mark_as_read():
    if (id := request.args.get('id')) is None:
        return {
            'error': 400,
            'details': 'The request is missing the required "id" parameter.'
        }, 400

    if not (notification := notifications.fetch_one(id)):
        return {
            'error': 404,
            'details': 'The requested notification does not exist.'
        }, 404

    if notification.user_id != current_user.id:
        return {
            'error': 403,
            'details': 'You are not authorized to perform this action.'
        }, 403

    notifications.update(
        id,
        {'read': True}
    )

    return {'success': True}
